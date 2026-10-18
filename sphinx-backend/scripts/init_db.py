import os
import sys

# Ensure root workspace directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import Role, User, Patient, MedicalRecord, Appointment, SearchIndex, AuditLog, BillingRecord

def init_database():
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)
    with app.app_context():
        print("Creating all database tables for Project SPHINX...")
        db.create_all()
        # Safe non-destructive column additions for existing tables
        from sqlalchemy import inspect, text
        insp = inspect(db.engine)
        if 'users' in insp.get_table_names():
            user_cols = {c['name'] for c in insp.get_columns('users')}
            if 'failed_login_count' not in user_cols:
                print("Adding missing column 'failed_login_count' to users table...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN failed_login_count INT DEFAULT 0"))
            if 'last_login_at' not in user_cols:
                print("Adding missing column 'last_login_at' to users table...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN last_login_at DATETIME NULL"))
            db.session.commit()
        print("Database schema successfully verified/created!")

if __name__ == '__main__':
    init_database()

