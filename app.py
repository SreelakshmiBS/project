from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_migrate import Migrate
from extensions import db
from models import *
from datetime import datetime, date
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret-key"

# --- Base Directory ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# --- Upload Configuration ---
VIDEO_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads/videos')
PROFILE_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/photos')
MATERIAL_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads/materials')

# Create folders if they don't exist
os.makedirs(VIDEO_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROFILE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MATERIAL_UPLOAD_FOLDER, exist_ok=True)

# Allowed video extensions
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'webm'}
ALLOWED_MATERIALS = {'pdf', 'docx', 'pptx', 'ppt', 'zip', 'txt', 'jpg', 'jpeg', 'png'}

# Configure app
app.config['UPLOAD_FOLDER_VIDEOS'] = VIDEO_UPLOAD_FOLDER       # For recorded videos
app.config['UPLOAD_FOLDER_PHOTOS'] = PROFILE_UPLOAD_FOLDER    # For profile photos
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024 # 1 GB limit for videos
app.config["MATERIAL_FOLDER"] = MATERIAL_UPLOAD_FOLDER

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# --- Initialize DB and Migrations ---
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/student')
def student_index():
    return render_template("student_index.html")

@app.route('/teacher')
def teacher_index():
    return render_template("teacher_index.html")

@app.route('/parent')
def parent_index():
    return render_template("parent_index.html") 

@app.route('/admin') 
def admin_index():
    return render_template("admin_index.html")

@app.route('/register', methods=['GET', 'POST'])
def student_registration():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        age = int(request.form['age'])
        grade = request.form['grade']
        course_id = request.form.get('course_id')  # dropdown sends subject_id

        # Check if student already exists
        exist = Student.query.filter_by(email=email).first()
        if exist:
            flash("User already exists", "danger")
            return redirect(url_for('home'))

        # Handle parent if student is under 18
        parent_id = None
        if age < 18:
            parent_name = request.form['parent_name']
            parent_contact = request.form['parent_contact']
            parent = Parent(
                name=parent_name,
                contact=parent_contact,
                email=None,
                password=None,
                child_name=name,
                relation_to_student=None,
                address=None
            )
            db.session.add(parent)
            db.session.flush()  # get parent.id without committing
            parent_id = parent.id

        # Create new student
        new_student = Student(
            name=name,
            email=email,
            password=password,
            age=age,
            grade=grade,
            course_id=course_id,
            parent_id=parent_id
        )

        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('login'))

    # GET request: fetch subjects from database
    courses =Course.query.all()
    return render_template("student_register.html", courses=courses)

        
@app.route('/students')
def students():
    all_students = Student.query.all()
    return render_template('student.html', students=all_students)  # for admin 

@app.route('/teacher_register', methods=['GET', 'POST'])
def teacher_registration():
    courses = Course.query.all()
    if request.method == 'POST':
        course_id = request.form['course']
        # Get form fields
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        qualifications = request.form.get('qualifications')
        availability = request.form.get('availability')
        years_of_experience = request.form.get('years_of_experience')
        contact = request.form.get('contact')
        place = request.form.get('place')
        
        

        # Handle photo upload
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename != "":
            filename = secure_filename(photo_file.filename)
            photo_file.save(os.path.join(app.config['UPLOAD_FOLDER_PHOTOS'], filename))
        else:
            filename = "default.jpg"

        # Create teacher record
        new_teacher = Teacher(
            name=name,
            email=email,
            password=password,  # hash in production!
            qualifications=qualifications,
            course_id=course_id,
            availability=availability,
            years_of_experience=years_of_experience,
            contact=contact,
            place=place,
            photo=filename
        )

        db.session.add(new_teacher)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("teacher_register.html",courses=courses)


@app.route('/teachers')
def teachers():
    all_teachers = Teacher.query.all()
    return render_template('teacher.html', students=all_teachers)  # for admin 


@app.route('/parent_register', methods=['GET', 'POST'])
def parent_registration():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        child_name = request.form['child_name']
        relation_to_student = request.form['relation_to_student']
        address = request.form['address']
        contact = request.form['contact']
        
        
        exist = Parent.query.filter_by(email=email).first()
        if exist:
            flash("User already exists")
            return redirect(url_for('home'))

        # create new teacher
        new_parent = Parent(
            name=name,
            email=email,
            password=password,
            child_name=child_name,
            relation_to_student=relation_to_student,
            address=address,
            contact=contact
        )

        db.session.add(new_parent)
        db.session.commit()
        # flash("Registration Successful")
        return redirect(url_for('login'))

    return render_template("parent_register.html")

@app.route('/parents')
def parents():
    all_parents = Parent.query.all()
    return render_template('parent.html', students=all_parents)  # for admin 


#login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # check in Student table
        student = Student.query.filter_by(email=email, password=password).first()
        if student:
            session['student_id'] = student.id 
            return redirect(url_for('student_dashboard'))

        # check in Teacher table
        teacher = Teacher.query.filter_by(email=email, password=password).first()
        if teacher:
            session['teacher_id'] = teacher.id
            return redirect(url_for('teacher_dashboard'))

        # check in Parent table
        parent = Parent.query.filter_by(email=email, password=password).first()
        if parent:
            session['parent_id'] = parent.id
            return redirect(url_for('parent_index'))

        # if no match found
        else:
            return render_template('invalid_login.html')

    return render_template('login.html')


@app.route('/invalid_login')
def invalid_login():
    return render_template('invalid_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

#Dashboard  
@app.route('/teacher_dashboard')
def teacher_dashboard():
    teacher_id = session.get('teacher_id')
    if not teacher_id:
        return redirect(url_for('login'))
    teacher = Teacher.query.get(teacher_id)
    current_date = datetime.now().strftime('%B %d, %Y')
    return render_template('teacher_dashboard.html', current_date=current_date,datetime=datetime,teacher =teacher)


@app.route('/student_dashboard')
def student_dashboard():
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('login'))
    student = Student.query.get(student_id)
    current_date = datetime.now().strftime('%B %d, %Y')
    attendence = Attendance.query.filter_by(student_id=student_id).all()
    return render_template('student_dashboard.html', current_date=current_date,datetime=datetime,student =student,attendence = attendence)
    
@app.route('/student_profile')
def student_profile():
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for('login'))
    student = Student.query.get(student_id)
    return render_template('student_profile.html', student=student)

@app.route('/teacher_profile')
def teacher_profile():
    teacher_id = session.get("teacher_id")
    if not teacher_id:
        return redirect(url_for('login'))
    teacher = Teacher.query.get(teacher_id)
    return render_template('teacher_profile.html', teacher=teacher)


@app.route('/teacher_edit_profile', methods=['GET', 'POST'])
def teacher_edit_profile():
    teacher_id = session.get("teacher_id")
    if not teacher_id:
        return redirect(url_for('login'))

    teacher = Teacher.query.get(teacher_id)

    if request.method == 'POST':
        
        # Handle Photo Upload
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename != "":
            filename = secure_filename(photo_file.filename)
            photo_file.save(os.path.join("static/photos", filename))
            teacher.photo = filename

        # Update Text Fields
        teacher.name = request.form['name']
        teacher.email = request.form['email']
        teacher.password = request.form['password']
        teacher.qualifications = request.form['qualifications']
        teacher.subject = request.form['subject']
        teacher.availability = request.form['availability']
        teacher.years_of_experience = request.form['years_of_experience']
        teacher.contact = request.form['contact']
        teacher.place = request.form['place']

        db.session.commit()
        return redirect(url_for('teacher_profile'))

    return render_template("teacher_edit_profile.html", teacher=teacher)


@app.route('/student_edit_profile', methods=['GET', 'POST'])
def student_edit_profile():
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for('login'))

    student = Student.query.get(student_id)

    if request.method == 'POST':

        # Update text fields
        student.name = request.form['name']
        student.email = request.form['email']
        student.password = request.form['password']
        student.age = request.form['age']
        student.grade = request.form['grade']
        student.parent_name = request.form['parent_name']
        student.parent_contact = request.form['parent_contact']
        student.course = request.form['course']
       
        db.session.commit()
        return redirect(url_for('student_profile'))

    return render_template("student_edit_profile.html", student=student)


@app.route('/parent_edit_profile', methods=['GET', 'POST'])
def parent_edit_profile():
    parent_id = session.get("parent_id")
    if not parent_id:
        return redirect(url_for('login'))

    parent = Parent.query.get(parent_id)

    if request.method == 'POST':

        # Update text fields
        parent.name = request.form['name']
        parent.email = request.form['email']
        parent.password = request.form['password']
        parent.Contact = request.form['contact']
        parent.place = request.form['place']

        db.session.commit()
        return redirect(url_for('parent_profile'))

    return render_template("parent_edit_profile.html", parent=parent)


@app.route('/teacher/attendance', methods=['GET', 'POST'])
def mark_attendance():
    teacher_id = session.get('teacher_id')

    if not teacher_id:
        return redirect(url_for('login'))

    students = Student.query.all()

    formatted_date = date.today().strftime("%d-%m-%Y")

    if request.method == 'POST':
        for student in students:
            status = request.form.get(f'status_{student.id}')
            if status:
                new_attendance = Attendance(
                    student_id=student.id,
                    teacher_id=teacher_id,
                    status=status,
                    date=date.today()
                )
                db.session.add(new_attendance)

        db.session.commit()
        return render_template('attendence.html', students=students, today=formatted_date, success=True)

    return render_template('attendence.html', students=students, today=formatted_date, success=False)


@app.route('/manage_class')
def manage_class():
    # You can fetch recorded and live classes from DB
    recorded_classes = Recorded_class.query.filter_by(teacher_id=session['teacher_id']).all()
    live_classes = Live_class.query.filter_by(teacher_id=session['teacher_id']).all()
    return render_template('manage_class.html', 
                           recorded_classes=recorded_classes,
                           live_classes=live_classes)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/teacher/upload_recorded_class', methods=['GET', 'POST'])
def upload_recorded_class():
    teacher_id = session.get("teacher_id")
    if not teacher_id:
        flash("Login required!", "danger")
        return redirect(url_for("login"))

    teacher = Teacher.query.get_or_404(teacher_id)
    
    # Teacher's courses (wrap in list if single)
    courses = [teacher.course] if teacher.course else []  
    if request.method == 'GET':
        return render_template("upload_recorded_class.html", courses=courses)

    # POST
    title = request.form.get("title")
    date_str = request.form.get("date")
    video = request.files.get("video")
    course_id = request.form.get("course_id")

    if not course_id:
        flash("Please select a course!", "danger")
        return redirect(url_for("upload_recorded_class"))

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format!", "danger")
        return redirect(url_for("upload_recorded_class"))

    if not video or video.filename == "":
        flash("Please upload a video!", "danger")
        return redirect(url_for("upload_recorded_class"))

    filename = secure_filename(video.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER_VIDEOS'], filename)
    video.save(save_path)

    # Save to database
    new_recorded = Recorded_class(
        teacher_id=teacher_id,
        course_id=course_id,
        title=title,
        date=date_obj,
        filename=filename
    )
    db.session.add(new_recorded)
    db.session.commit()

    flash("Recorded class uploaded successfully!", "success")
    return redirect(url_for("manage_class"))


@app.route('/teacher/upload_live_class', methods=['GET', 'POST'])
def upload_live_class():
    teacher_id = session.get("teacher_id")
    if not teacher_id:
        flash("Login required!", "danger")
        return redirect(url_for("login"))

    teacher = Teacher.query.get_or_404(teacher_id)
    
    # Teacher's courses
    courses = [teacher.course] if teacher.course else []
    if request.method == 'GET':
        return render_template("add_live_class.html", courses=courses)

    # POST
    title = request.form.get("title")
    date_str = request.form.get("date")
    time_str = request.form.get("time")
    platform = request.form.get("platform")
    link = request.form.get("link")
    course_id = request.form.get("course_id")

    if not course_id:
        flash("Please select a course!", "danger")
        return redirect(url_for("upload_live_class"))

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        time_obj = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        flash("Invalid date or time format!", "danger")
        return redirect(url_for("upload_live_class"))

    new_class = Live_class(
        teacher_id=teacher_id,
        course_id=course_id,
        title=title,
        date=date_obj,
        time=time_obj,
        platform=platform,
        link=link
    )
    db.session.add(new_class)
    db.session.commit()

    flash("Live class scheduled successfully!", "success")
    return redirect(url_for("manage_class"))


@app.route('/teacher/delete_recorded_class/<int:id>', methods=['GET'])
def delete_recorded_class(id):
    cls = Recorded_class.query.get_or_404(id)
    # Delete video file from storage
    file_path = os.path.join(app.config['UPLOAD_FOLDER_VIDEOS'], cls.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(cls)
    db.session.commit()

    return redirect(url_for('manage_class'))


@app.route('/edit_recorded_class/<int:id>', methods=['GET', 'POST'])
def edit_recorded_class(id):
    cls = Recorded_class.query.get_or_404(id)

    if request.method == 'POST':
        cls.title = request.form['title']
        cls.date = datetime.strptime(request.form['date'], "%Y-%m-%d").date()
        cls.filename = request.form['filename']

        db.session.commit()
        return redirect(url_for('manage_class'))

    return render_template('edit_recorded_cls.html', cls=cls)

@app.route('/edit_live-class/<int:id>', methods=['GET', 'POST'])
def edit_live_class(id):
    cls = Live_class.query.get_or_404(id)

    if request.method == 'POST':
        cls.title = request.form['title']
        cls.date = datetime.strptime(request.form['date'], "%Y-%m-%d").date()

        time_str = request.form['time']
        if len(time_str) == 5:
            cls.time = datetime.strptime(time_str, "%H:%M").time()
        else:
            cls.time = datetime.strptime(time_str, "%H:%M:%S").time()

        cls.platform = request.form['platform']
        cls.link = request.form['link']

        db.session.commit()
        return redirect(url_for('manage_class'))

    return render_template('edit_live_cls.html', cls=cls)

@app.route('/delete_live_class/<int:id>',methods =['GET'])
def delete_live_class(id):
    cls = Live_class.query.get_or_404(id)
    db.session.delete(cls)
    db.session.commit()
    return redirect(url_for('manage_class'))

def allowed_material(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_MATERIALS

@app.route('/upload_material', methods=['GET', 'POST'])
def upload_material():

    teacher_id = session.get('teacher_id')
    if not teacher_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        subject = request.form['subject']
        title = request.form['title']
        description = request.form['description']
        file = request.files['file']

        if file and allowed_material(file.filename):
            filename = secure_filename(file.filename)

            filepath = os.path.join(app.config['MATERIAL_FOLDER'], filename)
            file.save(filepath)

            material = Studymaterial(
                subject=subject, 
                teacher_id=teacher_id,    
                title=title,
                description=description,
                filename=filename,
                upload_date=date.today()
            )

            db.session.add(material)
            db.session.commit()

            return redirect(url_for('manage_materials'))
    subjects = Course.query.filter_by(teacher_id=teacher_id).all()
    return render_template("upload_materials.html", subjects=subjects)




@app.route('/manage_materials')
def manage_materials():
    teacher_id = session.get('teacher_id')
    materials = Studymaterial.query.filter_by(teacher_id=teacher_id).all()
    return render_template('manage_materials.html', materials=materials)

@app.route('/edit_material/<int:id>', methods=['GET', 'POST'])
def edit_material(id):
    material = Studymaterial.query.get_or_404(id)

    if request.method == 'POST':
        material.title = request.form['title']
        material.description = request.form['description']
        db.session.commit()
        return redirect(url_for('manage_materials'))

    return render_template("edit_material.html", material=material)


@app.route('/delete_material/<int:id>')
def delete_material(id):
    material = Studymaterial.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    return redirect(url_for('manage_materials'))

@app.route('/view_material_student/<int:id>')
def view_material_student(id):
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('student_login'))

    material = Studymaterial.query.get_or_404(id)

    # mark progress
    progress = Progress.query.filter_by(student_id=student_id, material_id=id).first()
    if not progress:
        new_progress = Progress(student_id=student_id, material_id=id, viewed=True)
        db.session.add(new_progress)
        db.session.commit()

    # open file
    return render_template("view_material_student.html", material=material)

@app.route('/student_progress')
def student_progress():
    student_id = session.get('student_id')  

    total_materials = Studymaterial.query.count()
    viewed_materials = Progress.query.filter_by(student_id=student_id, viewed=True).count()
    progress_percent = (viewed_materials / total_materials) * 100 if total_materials > 0 else 0

    return render_template("student_progress.html", progress=round(progress_percent))

@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        subject_name = request.form.get('subject')
        description = request.form.get('description')

        # Check empty input
        if not subject_name:
            flash("Subject name cannot be empty!", "danger")
            return redirect(url_for('add_subject'))

        # Save to DB
        new_subject = Course(name=subject_name,
                             description=description)
        
        db.session.add(new_subject)
        db.session.commit()

        flash("Subject added successfully!", "success")
        return redirect(url_for('add_subject'))

    return render_template('add_subject.html') #for admin

def add_courses():
    courses_list = [
        {"name": "Introduction to Robotics", "description": "Basics of Robotics"},
        {"name": "Embedded Systems", "description": "Learn microcontrollers"},
        {"name": "Artificial Intelligence", "description": "AI Concepts"},
        {"name": "Machine Learning", "description": "ML Algorithms"},
        {"name": "Python Programming", "description": "Learn Python"},
        {"name": "IoT Applications", "description": "IoT Projects"},
        {"name": "Computer Vision", "description": "CV Techniques"},
        {"name": "Cloud Computing", "description": "Cloud Concepts"}
    ]

    for c in courses_list:
        existing_course = Course.query.filter_by(name=c['name']).first()
        if not existing_course:
            db.session.add(Course(name=c['name'], description=c['description']))

    db.session.commit()
    
@app.route('/student/view_classes')
def student_view_classes():
    student_id = session.get("student_id")
    if not student_id:
        flash("Please login first!", "danger")
        return redirect(url_for("login"))

    # Get student
    student = Student.query.get_or_404(student_id)

    # If student has a course assigned
    course_id = student.course_id

    # Get recorded classes for student's course
    recorded_classes = Recorded_class.query.filter_by(course_id=course_id).all()

    # Get live classes for student's course
    live_classes = Live_class.query.filter_by(course_id=course_id).all()

    return render_template(
        "student_classes.html",
        recorded_classes=recorded_classes,
        live_classes=live_classes
    )


@app.route('/student/attendance')
def view_attendance():
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('login'))


    records = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.date).all()

    if not records:
        return render_template('student_attendance.html', records=[], percentage=0)

    # Prepare data for template
    attendance_list = []
    present_count = 0

    for record in records:
        attendance_list.append({
            "date": record.date.strftime("%d-%m-%Y"),
            "status": record.status
        })
        if record.status.lower() == "present":
            present_count += 1

    total_days = len(records)
    attendance_percentage = (present_count / total_days) * 100

    return render_template(
        'student_attendance.html',
        records=attendance_list,
        percentage=attendance_percentage
    )
    

            












    








    

        
        

     
        
    

if __name__ == '__main__':
    app.run(debug=True)