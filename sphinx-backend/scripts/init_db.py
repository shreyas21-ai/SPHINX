import os
import sys

# Ensure root workspace directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import Role, User, Patient, MedicalRecord, Appointment, SearchIndex, AuditLog

def init_database():
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)
    with app.app_context():
        print("Creating all database tables for Project SPHINX...")
        db.create_all()
        print("Database schema successfully created!")

if __name__ == '__main__':
    init_database()
