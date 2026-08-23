from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


class Company(db.Model):
    __tablename__ = "company"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    hr_contact = db.Column(db.String(20), nullable=False)
    website = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), nullable=False, default="Pending")
    is_blacklisted = db.Column(db.Boolean, default=False)
    drives = db.relationship("PlacementDrive", backref="company", lazy=True, cascade="all,delete-orphan")
# Note: Company.drives will give you a list of all placement drives associated with that company. The cascade option ensures that if a company is deleted, all its associated placement drives will also be deleted.
# backref contains name of reverse relationship, which will be added as a property to the related model (PlacementDrive in this case). So, you can access the company of a placement drive using drive.company.

class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    degree = db.Column(db.String(100), nullable=True)
    curriculum_vitae = db.Column(db.String(200), nullable=True)  
    is_blacklisted = db.Column(db.Boolean, default=False)
    skills = db.Column(db.String(300), nullable=True)

    applications = db.relationship("Application", backref="student", lazy=True, cascade="all,delete-orphan")


class PlacementDrive(db.Model):
    __tablename__ = "placement_drive"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=True)
    eligibility_criteria = db.Column(db.String(300), nullable=True)
    application_deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending") 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", backref="drive", lazy=True, cascade="all,delete-orphan")


class Application(db.Model):
    __tablename__ = "application"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drive.id"), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="Applied")  

    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="uix_student_drive"),
    )