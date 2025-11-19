from extensions import db



class Student(db.Model):
    __tablename__ = 'Student'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('Parent.id', name='fk_student_parent'))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('Course.id', name='fk_student_course'))
    course = db.relationship("Course")

    def __repr__(self):
        return f'<Student {self.name}>'

class Teacher(db.Model):
    __tablename__ = 'Teacher'
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(200), default='default.jpg')
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(100), nullable=False)
    qualifications = db.Column(db.String(200), nullable=False)
    availability = db.Column(db.String(100), nullable=False)
    years_of_experience = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    course = db.relationship("Course")
    
    course_id = db.Column(db.Integer, db.ForeignKey('Course.id', name='fk_teacher_course'))

    def __repr__(self):
        return f'<Teacher {self.name}>'

    
class Parent(db.Model):
    __tablename__ = 'Parent'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(100), nullable=True)
    child_name = db.Column(db.String(100), nullable=True)
    relation_to_student = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    contact = db.Column(db.String(20), nullable=False)
    
    student = db.relationship('Student', backref='parent', lazy=True)
    
class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., 'student', 'teacher', 'parent'
    
class Attendance(db.Model):
    __tablename__ = 'Attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('Student.id'))  
    teacher_id = db.Column(db.Integer, db.ForeignKey('Teacher.id'))  
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)
    student = db.relationship('Student', backref='attendance_records')
    teacher = db.relationship('Teacher', backref='marked_attendance')
    

class Recorded_class(db.Model):
    __tablename__ = 'Recorded_class'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('Teacher.id', name="fk_record_teacher"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('Course.id', name="fk_record_subject"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    filename = db.Column(db.String(300), nullable=False)

    teacher = db.relationship('Teacher', backref=db.backref('recorded_classes', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('recorded_classes', lazy='dynamic'))


class Live_class(db.Model):
    __tablename__ = 'Live_class'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('Teacher.id', name="fk_live_teacher"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('Course.id', name="fk_live_subject"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    platform = db.Column(db.String(100), nullable=True)
    link = db.Column(db.String(300), nullable=False)

    teacher = db.relationship('Teacher', backref=db.backref('live_classes', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('live_classes', lazy='dynamic'))

    def __repr__(self):
        return f"<LiveClass {self.title}>"
    
    
class Course(db.Model):
    __tablename__ = 'Course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    
    
# class Subject(db.Model):
#     __tablename__ = 'Subject'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)


    
class Studymaterial(db.Model):
    __tablename__ = 'Studymaterial'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('Teacher.id'))  
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(300), nullable=False)
    upload_date = db.Column(db.Date, nullable=False)

    teacher = db.relationship('Teacher', backref=db.backref('studymaterial', lazy=True))
    
class Progress(db.Model):
    __tablename__ = 'Progress'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('Student.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('Studymaterial.id'))
    viewed = db.Column(db.Boolean, default=False)

    student = db.relationship("Student", backref="progress")
    material = db.relationship("Studymaterial", backref="views")
    
# class StudentSubjects(db.Model):
#     __tablename__ = 'student_subjects'
    
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('Student.id', ondelete='CASCADE'), nullable=False)
#     subject_id = db.Column(db.Integer, db.ForeignKey('Subject.id', ondelete='CASCADE'), nullable=False)

#     # Relationships without conflicting backrefs
#     student = db.relationship('Student', back_populates='enrolled_subjects')
#     subject = db.relationship('Subject', back_populates='enrolled_students')

#     def __repr__(self):
#         return f"<StudentSubjects student_id={self.student_id} subject_id={self.subject_id}>"

  
    
       
    
