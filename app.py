
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from model import db, Admin, Company, Student, PlacementDrive, Application
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import or_

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sneh_dhaka'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    
db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/student_register', methods=["GET", "POST"])
def student_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        age = request.form.get('age')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        degree = request.form.get('degree')
        skills = request.form.get('skills')
        curriculum_vitae = request.form.get('curriculum_vitae')

        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('student_register'))

        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
            flash("Email already registered!")
            return redirect(url_for('student_register'))

        password_hash = generate_password_hash(password)

        student = Student(
            name=name, email=email, age=age, gender=gender, skills=skills, password_hash=password_hash, phone=phone,degree=degree, curriculum_vitae=curriculum_vitae
        )

        db.session.add(student)
        db.session.commit()

        flash("Student registered successfully!")
        return redirect(url_for('student_login'))

    return render_template('Student/student_register.html')

@app.route('/company_register', methods=["GET", "POST"])
def company_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        hr_contact = request.form.get('hr_contact')
        website = request.form.get('website')

        if password != confirm_password:
            flash("Passwords do not match. Please try again.")
            return redirect(url_for('company_register'))

        if Company.query.filter_by(email=email).first():
            flash("Email already registered. Please use a different email.")
            return redirect(url_for('company_register'))

        if Company.query.filter_by(name=name).first():
            flash("Company name already registered. Please use a different name.")
            return redirect(url_for('company_register'))

        company = Company(name=name, email=email, password_hash=generate_password_hash(password), hr_contact=hr_contact, website=website, approval_status="Pending", is_blacklisted=False
        )

        db.session.add(company)
        db.session.commit()

        flash("Company registered successfully! Please wait for admin approval.")
        return redirect(url_for('company_login'))

    return render_template('Company/company_register.html')

@app.route('/admin_login', methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = admin.id
            flash("Logged in successfully!")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid username or password. Please try again.")

    return render_template('Admin/admin_login.html')

@app.route('/company_login', methods=["GET", "POST"])
def company_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        company = Company.query.filter_by(email=email).first()
        if company and check_password_hash(company.password_hash, password):
            session['company_id'] = company.id
            flash("Logged in successfully!")
            return redirect('/company_dashboard')
        else:
            flash("Invalid email or password. Please try again.")

    return render_template('Company/company_login.html')

@app.route('/student_login', methods=["GET", "POST"])
def student_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        student = Student.query.filter_by(email=email).first()
        
        if student and check_password_hash(student.password_hash, password):
            session['student_id'] = student.id
            flash("Logged in successfully!")
            return redirect('/student_dashboard')
        else:
            flash("Invalid email or password. Please try again.")
            return redirect(url_for('student_login'))

    return render_template('Student/student_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash("Please login first.")
        return redirect(url_for('admin_login'))

    company_search = request.args.get('company_search', '')
    student_search = request.args.get('student_search', '')
    pending_companies = Company.query.filter_by(approval_status="Pending").all()
    pending_drives = PlacementDrive.query.filter_by(status="Pending").all()
    applications = Application.query.all()
    companies = Company.query.all()
    students = Student.query.all()
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()

    if company_search:
        companies = Company.query.filter(
            or_(
                Company.name.ilike(f"%{company_search}%"),
                Company.email.ilike(f"%{company_search}%")
            )
        ).all()
    else:
        companies = Company.query.all()

    if student_search:
        searched_students = Student.query.filter(
            or_(
                Student.name.ilike(f"%{student_search}%"),
                Student.email.ilike(f"%{student_search}%")
            )
        ).all()
    else:
        searched_students = Student.query.all()

    return render_template(
        'Admin/admin_dash.html',
        total_students = total_students,
        total_companies = total_companies,
        total_drives = total_drives,
        total_applications = total_applications,
        pending_companies=pending_companies,
        pending_drives=pending_drives,
        applications=applications,
        companies=companies,
        students=students,
        searched_students=searched_students,
        company_search=company_search,
        student_search=student_search
    )

@app.route('/approve_company/<int:company_id>')
def approve_company(company_id):
    if 'admin_id' not in session:
        flash("Please login first.")
        return redirect(url_for('admin_login'))

    company = Company.query.get_or_404(company_id)
    company.approval_status = "Approved"
    db.session.commit()
    flash("Company approved successfully!")
    return redirect(url_for('admin_dashboard'))


@app.route('/reject_company/<int:company_id>')
def reject_company(company_id):
    if 'admin_id' not in session:
        flash("Please login first.")
        return redirect(url_for('admin_login'))

    company = Company.query.get_or_404(company_id)
    company.approval_status = "Rejected"
    db.session.commit()
    flash("Company rejected successfully!")
    return redirect(url_for('admin_dashboard'))


@app.route('/blacklist_company/<int:company_id>')
def blacklist_company(company_id):
    if 'admin_id' not in session:
        flash("Please login first.")
        return redirect(url_for('admin_login'))

    company = Company.query.get_or_404(company_id)
    company.is_blacklisted = True
    db.session.commit()
    flash("Company blacklisted successfully!")
    return redirect(url_for('admin_dashboard'))


@app.route('/approve_drive/<int:drive_id>')
def approve_drive(drive_id):
    if 'admin_id' not in session:
        flash("Please login first.")
        return redirect(url_for('admin_login'))

    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Approved"
    db.session.commit()
    flash("Placement drive approved successfully!")
    return redirect(url_for('admin_dashboard'))


@app.route('/reject_drive/<int:drive_id>')
def reject_drive(drive_id):
    if 'admin_id' not in session:
        flash("Please login first.")
        return redirect(url_for('admin_login'))

    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Rejected"
    db.session.commit()
    flash("Placement drive rejected successfully!")
    return redirect(url_for('admin_dashboard'))


@app.route('/blacklist_student/<int:student_id>')
def blacklist_student(student_id):
    if 'admin_id' not in session:
        flash("Please login first.")
        return redirect(url_for('admin_login'))

    student = Student.query.get_or_404(student_id)
    student.is_blacklisted = True
    db.session.commit()
    flash("Student blacklisted successfully!")
    return redirect(url_for('admin_dashboard'))

@app.route('/company_dashboard')
def company_dashboard():
    if 'company_id' not in session:
        flash("Please login first.")
        return redirect(url_for('company_login'))

    company = Company.query.get(session['company_id'])

    if company.approval_status != "Approved":
        flash("Your company is not approved by admin.")
        return redirect(url_for('company_login'))

    if company.is_blacklisted:
        flash("Your company account has been blacklisted.")
        return redirect(url_for('company_login'))

    posted_drives = PlacementDrive.query.filter_by(
        company_id=company.id
    ).all()

    received_applications = Application.query.join(PlacementDrive).filter(
        PlacementDrive.company_id == company.id
    ).all()

    shortlisted_applications = Application.query.join(PlacementDrive).filter(
        PlacementDrive.company_id == company.id,
        Application.status.in_(["Shortlisted", "Selected"])
    ).all()

    return render_template(
        'Company/company_dash.html',
        company=company,
        posted_drives=posted_drives,
        received_applications=received_applications,
        shortlisted_applications=shortlisted_applications
    ) 

@app.route('/student_dashboard')
def student_dashboard():
    if 'student_id' not in session:
        flash("Please login first.")
        return redirect(url_for('student_login'))
    
    student = Student.query.get(session['student_id'])
    applications = Application.query.filter_by(student_id=student.id).all()
    search = request.args.get('search', '')
    applied_drive_ids = [app.drive_id for app in applications]

    if student.is_blacklisted:
        flash("Your account is deactivated.")
        return redirect(url_for('student_login'))
    
    approved_drives_query = PlacementDrive.query.join(Company).filter(
        PlacementDrive.status == "Approved",
        Company.approval_status == "Approved",
        Company.is_blacklisted == False
    )

    if search:
        approved_drives_query = approved_drives_query.filter(
            or_(
                Company.name.ilike(f"%{search}%"),
                PlacementDrive.job_title.ilike(f"%{search}%"),
                PlacementDrive.eligibility_criteria.ilike(f"%{search}%")
            )
        )

    approved_drives = approved_drives_query.all()
    

    return render_template(
        'Student/student_dash.html',
        student=student,
        search=search,
        approved_drives=approved_drives,
        applied_drive_ids=applied_drive_ids,
        applications=applications,
    )

@app.route('/apply_job/', methods=["POST"])
def apply_job():
    drive_id = request.form.get('drive_id')

    if not drive_id:
        flash("Invalid job request.")
        return redirect(url_for('student_dashboard'))

    drive_id = int(drive_id)
    if 'student_id' not in session:
        flash("Please login first.")
        return redirect(url_for('student_login'))

    student = Student.query.get(session['student_id'])
    
    applications = Application.query.filter_by(student_id=student.id).all()
    applied_drive_ids = [app.drive_id for app in applications]
    
    if student.is_blacklisted:
        flash("Your account is deactivated.")
        return redirect(url_for('student_dashboard'))

    existing_application = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()

    if existing_application:
        flash("You have already applied for this job.")
        return redirect(url_for('student_dashboard'))

    application = Application(
        student_id=student.id,
        drive_id=drive_id,
        status="Applied"
    )
    
    db.session.add(application)
    db.session.commit()

    flash("Applied successfully!")
    return redirect(url_for('student_dashboard'))

@app.route('/student_dashboard/student_profile', methods=["GET", "POST"])
def student_profile():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))
    student = Student.query.get(session['student_id'])
    if request.method == 'POST':
        student.name = request.form.get('name')
        student.email = request.form.get('email')
        student.phone = request.form.get('phone')
        student.degree = request.form.get('degree')
        student.skills = request.form.get('skills')
        student.curriculum_vitae = request.form.get('curriculum_vitae')

        db.session.commit()
        flash("Profile updated successfully!")
        return redirect(url_for('student_dashboard'))

    return render_template('Student/student_profile.html',student=student)

@app.route('/create_drives', methods=["GET", "POST"])
def create_drives():
    if 'company_id' not in session:
        flash("Please login first.")
        return redirect(url_for('company_login'))

    if request.method == "POST":
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        eligibility_criteria = request.form.get('eligibility_criteria')
        application_deadline = request.form.get('application_deadline')
        application_deadline = datetime.strptime(application_deadline, '%Y-%m-%d').date()

        drive = PlacementDrive(
            company_id=session['company_id'],
            job_title=job_title,
            job_description=job_description,
            eligibility_criteria=eligibility_criteria,
            application_deadline=application_deadline,
            status="Pending"   # admin will approve
        )

        db.session.add(drive)
        db.session.commit()

        flash("Job posted successfully! Waiting for admin approval.")
        return redirect(url_for('company_dashboard'))

    return render_template('Company/create_drives.html')

@app.route('/close_drive/<int:drive_id>')
def close_drive(drive_id):
    if 'company_id' not in session:
        return redirect(url_for('company_login'))
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Closed"
    db.session.commit()
    flash("Drive closed successfully!")
    return redirect(url_for('company_dashboard'))

@app.route('/delete_drive/<int:drive_id>')
def delete_drive(drive_id):
    if 'company_id' not in session:
        return redirect(url_for('company_login'))
    drive = PlacementDrive.query.get_or_404(drive_id)
    db.session.delete(drive)
    db.session.commit()
    flash("Drive deleted")
    return redirect(url_for('company_dashboard'))

@app.route('/update_application_status/<int:app_id>/<string:status>')
def update_application_status(app_id, status):

    if 'company_id' not in session:
        return redirect(url_for('company_login'))

    application = Application.query.get_or_404(app_id)

    application.status = status
    db.session.commit()

    flash("Application status updated!")
    return redirect(url_for('company_dashboard'))

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        existing_admin = Admin.query.filter_by(username='admin').first()

        if existing_admin:
            print("Admin already exists")

        else:
            admin = Admin(
            username='admin',
            email='admin@gmail.com',
            password_hash=generate_password_hash('admin123')
            )

            db.session.add(admin)
            db.session.commit()
            print("Admin created successfully. Please login with username: admin and password: admin123")
    app.run(debug=True)
