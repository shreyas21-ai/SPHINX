"""
Focused tests for Activity Monitoring (Requirement 8).

Tests:
  1. Failed login counter increments on bad password.
  2. Counter resets on successful login.
  3. Repeated-failure alert fires at threshold.
  4. Excessive-search alert fires above threshold (threshold-rule path).
  5. Off-hours login alert fires for an event logged at an off-hours timestamp.
  6. Alert endpoint returns 403 for non-admin users.
  7. Alert endpoint returns 200 with expected structure for admin users.
  8. Download alerts stub returns empty list and limitation notice.

No patient medical content, passwords, or encryption keys appear in assertions.
"""
import pytest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from app.models.role import Role
from app.models.user import User
from app.models.audit_log import AuditLog
from app.extensions import db
from app.services.activity_monitor_service import ActivityMonitorService
from app.services.auth_service import AuthService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def monitor_users(app):
    """Create an admin, a doctor, and a nurse used across all monitoring tests."""
    with app.app_context():
        roles = {r.name: r.id for r in Role.query.all()}
        users = {}
        specs = [
            ('mon_admin@sphinx.test', 'Admin', Role.ADMIN),
            ('mon_doctor@sphinx.test', 'Doctor', Role.DOCTOR),
            ('mon_nurse@sphinx.test', 'Nurse', Role.NURSE),
        ]
        for email, fname, rname in specs:
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(email=email, first_name=fname, last_name='Monitor',
                         role_id=roles[rname])
                u.set_password('MonPass123!')
                db.session.add(u)
            db.session.commit()
            users[rname] = User.query.filter_by(email=email).first().id
        return users


@pytest.fixture(scope='module')
def admin_token_monitor(app, monitor_users):
    with app.app_context():
        return create_access_token(identity=str(monitor_users[Role.ADMIN]))


@pytest.fixture(scope='module')
def doctor_token_monitor(app, monitor_users):
    with app.app_context():
        return create_access_token(identity=str(monitor_users[Role.DOCTOR]))


# ---------------------------------------------------------------------------
# 1. Failed login counter increments on wrong password
# ---------------------------------------------------------------------------

def test_failed_login_increments_counter(app, monitor_users):
    with app.app_context():
        user = User.query.get(monitor_users[Role.DOCTOR])
        initial = user.failed_login_count or 0

        # Attempt login with wrong password — expect UnauthorizedException
        from app.utils.exceptions import UnauthorizedException
        try:
            AuthService.authenticate_user(user.email, 'WRONG_PASSWORD_XYZ')
        except UnauthorizedException:
            pass  # expected

        # Re-fetch from DB to see committed value
        db.session.expire_all()
        user_after = User.query.get(monitor_users[Role.DOCTOR])
        assert user_after.failed_login_count == initial + 1, (
            f"Expected {initial + 1}, got {user_after.failed_login_count}"
        )


# ---------------------------------------------------------------------------
# 2. Counter resets on successful login
# ---------------------------------------------------------------------------

def test_successful_login_resets_counter(app, monitor_users):
    with app.app_context():
        user = User.query.get(monitor_users[Role.DOCTOR])
        # Manually set a non-zero counter
        user.failed_login_count = 4
        db.session.commit()

        # Successful login
        AuthService.authenticate_user(user.email, 'MonPass123!')

        db.session.expire_all()
        user_after = User.query.get(monitor_users[Role.DOCTOR])
        assert user_after.failed_login_count == 0
        assert user_after.last_login_at is not None


# ---------------------------------------------------------------------------
# 3. Repeated-failure alert fires when counter >= threshold
# ---------------------------------------------------------------------------

def test_repeated_failure_alert_at_threshold(app, monitor_users):
    with app.app_context():
        user = User.query.get(monitor_users[Role.DOCTOR])
        user.failed_login_count = 5        # exactly at default threshold
        db.session.commit()

        alerts = ActivityMonitorService.get_repeated_failure_alerts(threshold=5)
        matching = [a for a in alerts if a['user_email'] == user.email]
        assert len(matching) == 1, f"Expected 1 alert, got {len(matching)}"
        alert = matching[0]
        assert alert['alert_type'] == 'REPEATED_FAILED_LOGINS'
        assert alert['severity'] == 'HIGH'
        assert alert['detection_method'] == 'THRESHOLD_RULE'
        # Must not expose internal DB id or passwords
        assert 'password' not in str(alert).lower()
        # Clean up
        user.failed_login_count = 0
        db.session.commit()


# ---------------------------------------------------------------------------
# 4. Excessive-search alert fires above threshold (threshold-rule path)
# ---------------------------------------------------------------------------

def test_excessive_search_alert_threshold(app, monitor_users):
    with app.app_context():
        doctor_id = monitor_users[Role.DOCTOR]
        # Inject fake SEARCH audit entries for today
        for _ in range(25):
            log = AuditLog(
                user_id=doctor_id,
                user_role=Role.DOCTOR,
                action='HMAC_SEARCH',
                purpose='TREATMENT',
                ip_address='127.0.0.1',
                user_agent='pytest'
            )
            db.session.add(log)
        db.session.commit()

        alerts = ActivityMonitorService.get_excessive_search_alerts(threshold=20)
        doctor_user = User.query.get(doctor_id)
        matching = [a for a in alerts if a['user_email'] == doctor_user.email]
        assert len(matching) >= 1, f"Expected >=1 alert, got {len(matching)}"
        assert matching[0]['alert_type'] == 'EXCESSIVE_SEARCHES'
        assert matching[0]['severity'] == 'MEDIUM'
        assert matching[0]['detection_method'] in ('THRESHOLD_RULE', 'ISOLATION_FOREST')


# ---------------------------------------------------------------------------
# 5. Off-hours login alert fires for events at unusual hours
# ---------------------------------------------------------------------------

def test_off_hours_login_alert(app, monitor_users):
    with app.app_context():
        nurse_id = monitor_users[Role.NURSE]
        # Inject a LOGIN audit event timestamped at 03:00 UTC (off-hours)
        off_hours_ts = datetime.utcnow().replace(hour=3, minute=0, second=0, microsecond=0)
        log = AuditLog(
            user_id=nurse_id,
            user_role=Role.NURSE,
            action='LOGIN',
            purpose='GENERAL',
            ip_address='10.0.0.5',
            user_agent='pytest',
            timestamp=off_hours_ts
        )
        db.session.add(log)
        db.session.commit()

        alerts = ActivityMonitorService.get_off_hours_login_alerts()
        nurse_user = User.query.get(nurse_id)
        matching = [a for a in alerts if a['user_email'] == nurse_user.email]
        assert len(matching) >= 1, f"Expected >=1 off-hours alert, got {len(matching)}"
        assert matching[0]['alert_type'] == 'OFF_HOURS_LOGIN'
        assert matching[0]['severity'] == 'LOW'


# ---------------------------------------------------------------------------
# 6. Alert endpoint: non-admin receives 403
# ---------------------------------------------------------------------------

def test_alerts_endpoint_blocks_non_admin(client, doctor_token_monitor):
    res = client.get(
        '/api/v1/dashboard/alerts',
        headers={'Authorization': f'Bearer {doctor_token_monitor}'}
    )
    assert res.status_code == 403, f"Expected 403, got {res.status_code}"


# ---------------------------------------------------------------------------
# 7. Alert endpoint: admin receives 200 with expected structure
# ---------------------------------------------------------------------------

def test_alerts_endpoint_admin_success(client, admin_token_monitor):
    res = client.get(
        '/api/v1/dashboard/alerts',
        headers={'Authorization': f'Bearer {admin_token_monitor}'}
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.get_json()
    assert data['status'] == 'success'
    payload = data['data']
    assert 'total_alerts' in payload
    assert 'alerts' in payload
    assert 'summary' in payload
    assert 'limitations' in payload
    assert 'generated_at' in payload
    # Verify large_downloads stub is present with zero count
    assert payload['summary']['large_downloads'] == 0


# ---------------------------------------------------------------------------
# 8. Download alert stub returns empty list and limitation notice
# ---------------------------------------------------------------------------

def test_download_alerts_stub(app):
    with app.app_context():
        alerts = ActivityMonitorService.get_download_alerts()
        assert alerts == [], "Expected empty list — no download endpoint exists"

    # Verify get_all_alerts reports the limitation
    with app.app_context():
        result = ActivityMonitorService.get_all_alerts()
        assert any('download' in lim.lower() for lim in result['limitations'])


# ---------------------------------------------------------------------------
# 9. Duplicate alert prevention on repeated dashboard refreshes
# ---------------------------------------------------------------------------

def test_duplicate_prevention_on_repeated_refreshes(client, admin_token_monitor, app, monitor_users):
    """
    Verify that repeated calls/refreshes do not create duplicate alerts
    or inflate counts. Multiple events from the same user are deduplicated.
    """
    with app.app_context():
        # Inject multiple off-hours logins for the same user
        nurse_id = monitor_users[Role.NURSE]
        for hour in [1, 2, 3]:
            off_ts = datetime.utcnow().replace(hour=hour, minute=0, second=0, microsecond=0)
            db.session.add(AuditLog(
                user_id=nurse_id,
                user_role=Role.NURSE,
                action='LOGIN',
                purpose='GENERAL',
                ip_address='10.0.0.5',
                user_agent='pytest',
                timestamp=off_ts
            ))
        db.session.commit()

        # Call get_off_hours_login_alerts directly
        off_alerts = ActivityMonitorService.get_off_hours_login_alerts()
        nurse_user = User.query.get(nurse_id)
        nurse_alerts = [a for a in off_alerts if a['user_email'] == nurse_user.email]
        assert len(nurse_alerts) == 1, (
            f"Expected exactly 1 deduplicated alert for nurse, got {len(nurse_alerts)}"
        )

    # First fetch via admin endpoint
    res1 = client.get('/api/v1/dashboard/alerts', headers={'Authorization': f'Bearer {admin_token_monitor}'})
    assert res1.status_code == 200
    data1 = res1.get_json()['data']

    # Second fetch (refresh) via admin endpoint
    res2 = client.get('/api/v1/dashboard/alerts', headers={'Authorization': f'Bearer {admin_token_monitor}'})
    assert res2.status_code == 200
    data2 = res2.get_json()['data']

    # Counts must remain identical across refreshes
    assert data1['total_alerts'] == data2['total_alerts']
    assert data1['summary'] == data2['summary']
    assert len(data1['alerts']) == len(data2['alerts'])


# ---------------------------------------------------------------------------
# 10. Genuine Isolation Forest anomaly detection on synthetic activity
# ---------------------------------------------------------------------------

def test_genuine_isolation_forest_synthetic_data():
    """
    Verify that _try_isolation_forest uses genuine scikit-learn IsolationForest
    to detect statistical outliers on synthetic activity data (>=5 users).
    """
    from app.services.activity_monitor_service import _try_isolation_forest

    # Synthetic per-user search volume: 9 normal users (1-5 searches) and 1 high-volume outlier (250 searches)
    synthetic_counts = {
        101: 2,
        102: 3,
        103: 1,
        104: 4,
        105: 2,
        106: 5,
        107: 3,
        108: 2,
        109: 4,
        999: 250,  # Extreme outlier
    }

    flagged = _try_isolation_forest(synthetic_counts)
    assert 999 in flagged, f"Isolation Forest failed to flag extreme outlier 999. Flagged: {flagged}"
    # The normal users with ~2 searches should not all be flagged
    assert len(flagged) < len(synthetic_counts)

