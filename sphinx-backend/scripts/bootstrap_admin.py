import os
import sys

# Ensure root workspace directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.user import User
from app.services.patient_service import PatientService
from app.services.medical_record_service import MedicalRecordService
from app.services.appointment_service import AppointmentService

def bootstrap():
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)

    with app.app_context():
        print("Ensuring database tables exist...")
        db.create_all()

        print("Seeding system roles...")
        roles_data = [
            (Role.ADMIN, 'System Administrator'),
            (Role.DOCTOR, 'Licensed Medical Practitioner'),
            (Role.NURSE, 'Registered Clinical Nurse'),
            (Role.RECEPTIONIST, 'Patient Scheduling & Intake Staff'),
            (Role.INSURANCE_OFFICER, 'Insurance & Claims Representative')
        ]

        role_objs = {}
        for r_name, r_desc in roles_data:
            role = Role.query.filter_by(name=r_name).first()
            if not role:
                role = Role(name=r_name, description=r_desc)
                db.session.add(role)
                db.session.commit()
                print(f"Created Role: {r_name}")
            role_objs[r_name] = role

        admin_email = app.config['BOOTSTRAP_ADMIN_EMAIL']
        admin_pass = app.config['BOOTSTRAP_ADMIN_PASSWORD']

        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                first_name='Super',
                last_name='Admin',
                role_id=role_objs[Role.ADMIN].id
            )
            admin_user.set_password(admin_pass)
            db.session.add(admin_user)
            db.session.commit()
            print(f"Bootstrapped Admin Account: {admin_email}")
        else:
            print(f"Admin account already exists: {admin_email}")

        # Seed sample users for testing demo
        sample_users = [
            ('dr.smith@sphinxhealth.com', 'DoctorPass123!', 'Alice', 'Smith', Role.DOCTOR),
            ('nurse.john@sphinxhealth.com', 'NursePass123!', 'John', 'Doe', Role.NURSE),
            ('rec.sarah@sphinxhealth.com', 'RecPass123!', 'Sarah', 'Connor', Role.RECEPTIONIST),
            ('ins.mark@sphinxhealth.com', 'InsPass123!', 'Mark', 'Taylor', Role.INSURANCE_OFFICER),
        ]

        created_users = {}
        for email, passw, fname, lname, rname in sample_users:
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(email=email, first_name=fname, last_name=lname, role_id=role_objs[rname].id)
                u.set_password(passw)
                db.session.add(u)
                db.session.commit()
                print(f"Created sample user: {email} ({rname})")
            created_users[rname] = u

        # Seed sample patients & encrypted records if none exist
        if PatientService.list_patients(role_name='ADMIN') == []:
            print("Seeding sample encrypted patient records...")
            p1 = PatientService.create_patient({
                'first_name': 'Rav',
                'last_name': 'Kumar',
                'dob': '1985-04-12',
                'gender': 'Male',
                'phone': '+1-555-0199',
                'email': 'rav.kumar@example.com',
                'address': '123 Health Ave, Medical City',
                'insurance_provider': 'BlueShield Healthcare',
                'policy_number': 'POL-992811',
                'blood_group': 'O+'
            })

            p2 = PatientService.create_patient({
                'first_name': 'Eleanor',
                'last_name': 'Vance',
                'dob': '1992-09-24',
                'gender': 'Female',
                'phone': '+1-555-0244',
                'email': 'eleanor.vance@example.com',
                'address': '456 Wellness Blvd, Metro Area',
                'insurance_provider': 'Aetna Care',
                'policy_number': 'POL-448201',
                'blood_group': 'A-'
            })

            # Create sample medical record for Rav Kumar (Disease = Diabetes)
            doctor = created_users[Role.DOCTOR]
            MedicalRecordService.create_record({
                'patient_public_id': p1['public_id'],
                'disease': 'Diabetes Mellitus Type 2',
                'diagnosis': 'High fasting blood glucose levels, HbA1c 8.2%',
                'medical_history': 'Family history of diabetes and hypertension',
                'prescription': 'Metformin 500mg BD, Glipizide 5mg OD',
                'lab_reports': 'Fasting Glucose: 165 mg/dL, HbA1c: 8.2%',
                'doctor_notes': 'Patient advised to adhere to low glycemic index diet and daily exercise.',
                'insurance_details': 'Covered under chronic disease management program',
                'treatment_plan': 'Quarterly endocrine evaluation and blood sugar tracking',
                'allergies': 'Penicillin',
                'vitals': 'BP: 128/82 mmHg, Heart Rate: 72 bpm, BMI: 27.4'
            }, doctor_id=doctor.id)

            # Create sample appointment with doctor and nurse
            from datetime import datetime, timedelta
            AppointmentService.create_appointment({
                'patient_public_id': p1['public_id'],
                'doctor_public_id': doctor.public_id,
                'nurse_public_id': created_users[Role.NURSE].public_id,
                'appointment_date': (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'reason': 'Routine Endocrinology Follow-up'
            })

            # Create sample billing claim for Insurance Officer
            from app.services.billing_service import BillingService
            BillingService.create_billing_claim({
                'patient_public_id': p1['public_id'],
                'items': [
                    {'item_name': 'Endocrinology Consultation', 'quantity': 1, 'unit_price': 150.0},
                    {'item_name': 'HbA1c Lab Panel', 'quantity': 1, 'unit_price': 75.0},
                    {'item_name': 'Metformin 500mg Supply', 'quantity': 2, 'unit_price': 25.0}
                ],
                'approved_amount': 225.0,
                'insurance_provider': 'BlueShield Healthcare',
                'policy_number': 'POL-992811',
                'claim_notes': 'Primary consultation and routine lab panel covered under chronic disease benefit.'
            }, officer_id=created_users[Role.INSURANCE_OFFICER].id)

            print("Sample encrypted patients, medical records, appointments, and billing claims seeded successfully!")

        print("\n====================================================")
        print("Project SPHINX Bootstrap Completed Successfully!")
        print(f"Admin Username: {admin_email}")
        print(f"Admin Password: {admin_pass}")
        print("====================================================\n")

if __name__ == '__main__':
    bootstrap()
