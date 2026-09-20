import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.user import User
from flask_jwt_extended import create_access_token


@pytest.fixture(scope='module')
def app():
    _app = create_app('testing')
    with _app.app_context():
        db.create_all()
        # Seed roles
        for r_name in Role.ROLES_LIST:
            if not Role.query.filter_by(name=r_name).first():
                db.session.add(Role(name=r_name, description=f"Test {r_name}"))
        db.session.commit()
        yield _app
        db.session.remove()
        try:
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0;'))
            db.drop_all()
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1;'))
            db.session.commit()
        except Exception:
            db.drop_all()


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()


@pytest.fixture(scope='module')
def admin_user(app):
    with app.app_context():
        role = Role.query.filter_by(name=Role.ADMIN).first()
        u = User(email='testadmin@sphinx.com', first_name='Test', last_name='Admin', role_id=role.id)
        u.set_password('AdminPass123!')
        db.session.add(u)
        db.session.commit()
        user_id = u.id
    with app.app_context():
        return User.query.get(user_id)


@pytest.fixture(scope='module')
def doctor_user(app):
    with app.app_context():
        role = Role.query.filter_by(name=Role.DOCTOR).first()
        u = User(email='testdoctor@sphinx.com', first_name='Test', last_name='Doctor', role_id=role.id)
        u.set_password('DoctorPass123!')
        db.session.add(u)
        db.session.commit()
        user_id = u.id
    with app.app_context():
        return User.query.get(user_id)


@pytest.fixture(scope='module')
def nurse_user(app):
    with app.app_context():
        role = Role.query.filter_by(name=Role.NURSE).first()
        u = User(email='testnurse@sphinx.com', first_name='Test', last_name='Nurse', role_id=role.id)
        u.set_password('NursePass123!')
        db.session.add(u)
        db.session.commit()
        user_id = u.id
    with app.app_context():
        return User.query.get(user_id)


@pytest.fixture(scope='module')
def doctor_token(app, doctor_user):
    with app.app_context():
        return create_access_token(identity=str(doctor_user.id))


@pytest.fixture(scope='module')
def nurse_token(app, nurse_user):
    with app.app_context():
        return create_access_token(identity=str(nurse_user.id))
