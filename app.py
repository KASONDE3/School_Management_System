from flask import Flask, render_template, request, url_for, session, redirect, make_response
import mysql.connector
from flask_mysqldb import MySQL
from flask import flash
from m_key import key, s_key
import pdfkit
from spmsdb import db

app = Flask(__name__)

# Mysql configuration 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = key
app.config['MYSQL_DB'] = db

mysql = MySQL(app)
app.secret_key = s_key

# Pdfkit executable application route
path_wkhtmltopdf = r'C:\Users\KASONDE MUKUKA\Desktop\MAIN LAB\PYTHON WEB APPS\SPMS\wkhtmltox\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

# Routing 
@app.route('/')
# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admin_dt WHERE username = %s AND password = %s", (username, password))
        admin = cursor.fetchone()
        if admin:
            session['admin_id'] = admin[0]
            return redirect(url_for('dashboard'))
        else: 
            return render_template('login_error.html')
        
    return render_template('login.html')

# user login 
@app.route('/login_user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        ts_number = request.form['ts_number']
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        select_query = "SELECT ts_number FROM teacher WHERE ts_number = %s"
        cursor.execute(select_query, (ts_number,))
        result = cursor.fetchone()
        # if ts_number is found execute code block below
        if result:
            select_query = "SELECT username, password FROM user_login WHERE username = %s"
            cursor.execute(select_query, (username,))
            result = cursor.fetchone()
            
            if result and result[1] == password:
                user_id = result[0]
                session['user_id'] = user_id
                return render_template('dashboard.html')         
            flash('Invalid username or password')
        
        flash('Invalid ts_number')
    
    return render_template('login_user.html')

# DISPLAY ROUTES ONLY
# Fetch pupils route
@app.route('/display_pupils')
def display_pupils():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pupil")
    pupils = cursor.fetchall()
    cursor.close()
    return render_template('display_pupils.html', pupils=pupils)

# Display teaachers
@app.route('/display_teachers')
def display_teachers():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM teacher")
    teachers = cursor.fetchall()
    cursor.close()
    return render_template('display_teachers.html', teachers=teachers)

# Display results
@app.route('/display_results')
def display_results():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM results")
    results = cursor.fetchall()
    cursor.close()
    return render_template('display_results.html', results=results)

# Display Classrooms
@app.route('/display_classrooms')
def display_classrooms():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM classrooms")
    clrms = cursor.fetchall()
    cursor.close()
    
    return render_template('display_classrooms.html', clrms=clrms)

########## Display subjects  ##################
@app.route('/display_subjects')
def display_subjects():
    cursor = mysql.connection.cursor()
    cursor.execute("select * from subjects")
    sub = cursor.fetchall()
    cursor.close()
    
    return render_template('display_subjects.html', subjects=sub)
    

# DASHBOARD RENDERING ONLY 
@app.route('/dashboad')
def dashboard():
    return render_template('dashboard.html') 

# Pupil Dashboard
@app.route('/p_dash')
def p_dash():
    return render_template('p_dash.html')

# teacher dashboard 
@app.route('/t_dash')
def t_dash():
    return render_template('t_dash.html')

# admin dash
@app.route('/admin_dash')
def admin_dash():
    return render_template('admin_dash.html')

# Subject dashboard
@app.route('/subject_dash')
def subject_dash():
    return render_template('subject_dash.html')

# Classrooms dash
@app.route('/classroom_dash')
def classroom_dash():
    return render_template('classroom_dash.html')

# REGISTRATION ROUTES
############# PUPILS SECTION ################# 
# Pupil Registration
@app.route('/add_pupil', methods=['GET', 'POST'])
def add_pupil():
    if 'admin_id' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, name FROM classrooms")
        classrooms = cursor.fetchall()
        cursor.close()
        
        if request.method == 'POST':
            # Retrieve form data
            exam_number = request.form['exam_number']
            first_name = request.form['first_name']
            other_names = request.form['other_names']
            last_name = request.form['last_name']
            gender = request.form['gender']
            dob = request.form['dob']
            address = request.form['address']
            guardian_fn = request.form['guardian_fn']
            guardian_ln = request.form['guardian_ln']
            phone = request.form['phone']       
            classroom_id = request.form['classroom_id']     
            
            # Check if the pupil already exists based on exam_number
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM pupil WHERE exam_number = %s", (exam_number,))
            existing_pupil = cursor.fetchone()

            if existing_pupil:
                # Update the existing pupil
                return flash('Pupil already Exists')
            else:
                # Insert a new pupil
                cursor.execute("""
                    INSERT INTO pupil (exam_number, first_name,other_names, last_name, gender, dob, address, guardian_fn, guardian_ln, phone, classroom_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (exam_number, first_name,other_names, last_name, gender, dob, address, guardian_fn, guardian_ln, phone, classroom_id))

            mysql.connection.commit()

            return redirect(url_for('display_pupils'))

        return render_template('add_pupil.html', classrooms=classrooms)

    else:
        return redirect(url_for('login'))
 
# update pupil
@app.route('/edit_pupil/<int:exam_number>', methods=['GET'])
def edit_pupil(exam_number):
    # Retrieve the pupil from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pupil WHERE exam_number = %s", (exam_number,))
    pupil_tuple = cursor.fetchone()  # Fetch the pupil data from the database
    cursor.close()

    if pupil_tuple:
        # Convert tuple to dictionary
        keys = ['exam_number', 'first_name', 'other_names', 'last_name', 'gender', 'dob', 'address', 'guardian_fn', 'guardian_ln', 'phone', 'classroom_id']
        pupil = dict(zip(keys, pupil_tuple))
        return render_template('edit_pupil.html', pupil=pupil)
    else:
        flash('Pupil not found')
        return redirect(url_for('display_pupils'))



# Delete pupil
@app.route('/delete_pupil/<int:exam_number>', methods=['POST'])
def delete_pupil(exam_number):
    if 'admin_id' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM pupil WHERE exam_number = %s", (exam_number,))
        mysql.connection.commit()
        flash('Pupil deleted successfully')
        return redirect(url_for('display_pupils'))
    else:
        return redirect(url_for('login'))

@app.route('/update_pupil/<int:exam_number>', methods=['POST'])
def update_pupil(exam_number):
    if 'admin_id' in session:
        print(f"Received POST request to update pupil with exam_number: {exam_number}")
        print(f"Request form data: {request.form}")

        # Retrieve form data
        first_name = request.form.get('first_name')
        other_names = request.form.get('other_names')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        address = request.form.get('address')
        guardian_fn = request.form.get('guardian_fn')
        guardian_ln = request.form.get('guardian_ln')
        phone = request.form.get('phone')

        # Check if any of the required fields are missing
        if not all([first_name, last_name, gender, dob]):
            flash('Please fill out all required fields.')
            return redirect(url_for('edit_pupil', exam_number=exam_number))

        # Update the pupil's data
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE pupil
            SET first_name=%s, other_names=%s, last_name=%s, gender=%s, dob=%s, address=%s, guardian_fn=%s, guardian_ln=%s, phone=%s
            WHERE exam_number=%s
        """, (first_name, other_names, last_name, gender, dob, address, guardian_fn, guardian_ln, phone, exam_number))
        mysql.connection.commit()

        flash('Pupil updated successfully')
        return redirect(url_for('display_pupils'))
    else:
        return redirect(url_for('login'))

########### TEACHER SECTION #######################
@app.route('/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        ts_number = request.form['ts_number']
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        gender = request.form['gender']
        nrc = request.form['nrc']
        phone = request.form['phone']
        email = request.form['email']
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO teacher (ts_number,f_name, l_name, gender, nrc, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (ts_number, f_name, l_name, gender, nrc, phone, email))
        mysql.connection.commit()
        cursor.close()
        
        flash('Teacher added successfully')
        return redirect(url_for('display_teachers'))
    return render_template('add_teacher.html')


@app.route('/edit_teacher/<int:ts_number>', methods=['GET', 'POST'])
def edit_teacher(ts_number):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM teacher WHERE ts_number = %s", (ts_number,))
    teacher = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        gender = request.form['gender']
        nrc = request.form['nrc']
        phone = request.form['phone']
        email = request.form['email']
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE teacher
            SET f_name = %s, l_name = %s, gender = %s, nrc = %s, phone = %s, email = %s
            WHERE ts_number = %s
        """, (f_name, l_name, gender, nrc, phone, email, ts_number))
        mysql.connection.commit()
        cursor.close()
        
        flash('Teacher updated successfully')
        return redirect(url_for('display_teachers'))
    return render_template('edit_teacher.html', teacher=teacher)


@app.route('/delete_teacher/<int:ts_number>', methods=['POST'])
def delete_teacher(ts_number):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM teacher WHERE ts_number = %s", (ts_number,))
    mysql.connection.commit()
    cursor.close()
    
    flash('Teacher deleted successfully')
    return redirect(url_for('display_teachers'))
 

############### Enter results section  #################
# holder 
@app.route('/results_dash')
def results_dash():
    return render_template('results_dash.html')

# new add result per term 
@app.route('/index2')
def index2():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM classrooms")
    classrooms = cur.fetchall()
    cur.close()
    return render_template('index2.html', classrooms=classrooms)


@app.route('/add_result', methods=['GET', 'POST'])
def add_result():
    if request.method == 'POST':
        exam_number = request.form['exam_number']
        subject_id = request.form['subject_id']
        ts_number = request.form['ts_number']
        marks = request.form['marks']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO results (exam_number, subject_id, ts_number, marks) VALUES (%s, %s, %s, %s)", (exam_number, subject_id, ts_number, marks))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index2'))
    return render_template('add_result.html')

@app.route('/results')
def results():
    cur = mysql.connection.cursor()
    cur.execute("SELECT pupil.exam_number, subjects.subject_id, teacher.ts_number, results.marks FROM results JOIN pupil ON results.exam_number = pupil.exam_number JOIN subjects ON results.subject_id = subjects.subject_id JOIN teacher ON results.ts_number = teacher.ts_number")
    data = cur.fetchall()
    cur.close()
    return render_template('results.html', results=data)

@app.route('/report_card/<int:exam_number>')
def report_card(exam_number):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT pupil.exam_number, subjects.subject_id, subjects.name, results.marks 
        FROM results 
        JOIN pupil ON results.exam_number = pupil.exam_number 
        JOIN subjects ON results.subject_id = subjects.subject_id
        WHERE pupil.exam_number = %s
    """, (exam_number,))
    data = cur.fetchall()
    cur.close()
    return render_template('report_card.html', report=data)


@app.route('/enter_results/<int:classroom_id>', methods=['GET', 'POST'])
def enter_results(classroom_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT exam_number FROM pupil WHERE classroom_id = %s", (classroom_id,))
    pupils = cur.fetchall()
    cur.close()
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    cursor.close()
    
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        ts_number = request.form['ts_number']
        for pupil in pupils:
            exam_number = pupil[0]
            marks = request.form.get(f'marks_{exam_number}')
            if marks:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO results (exam_number, subject_id, ts_number, marks) VALUES (%s, %s, %s, %s)",
                            (exam_number, subject_id, ts_number, marks))
                mysql.connection.commit()
                cur.close()
        return redirect(url_for('index2'))

    return render_template('enter_results.html', pupils=pupils, subjects=subjects, classroom_id=classroom_id)

#########   UPDATE RESULTS    ###################
# Edit results 
@app.route('/edit_result/<int:exam_number>/<int:subject_id>', methods=['GET', 'POST'])
def edit_result(exam_number, subject_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT marks 
        FROM results 
        WHERE exam_number = %s AND subject_id = %s
    """, (exam_number, subject_id))
    result = cur.fetchone()
    cur.close()
    
    if request.method == 'POST':
        new_marks = request.form['marks']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE results 
            SET marks = %s 
            WHERE exam_number = %s AND subject_id = %s
        """, (new_marks, exam_number, subject_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('report_card', exam_number=exam_number))

    return render_template('edit_result.html', result=result, exam_number=exam_number, subject_id=subject_id)

# delete results 
@app.route('/delete_result/<int:exam_number>/<int:subject_id>', methods=['POST'])
def delete_result(exam_number, subject_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        DELETE FROM results 
        WHERE exam_number = %s AND subject_id = %s
    """, (exam_number, subject_id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('report_card', exam_number=exam_number))

#########  CLASSROOM SECTION  #############
@app.route('/add_classrooms', methods=['GET', 'POST'])
def add_classrooms():
    if 'admin_id' in session:
        
        if request.method == 'POST':
            # Retrieve form data
            name = request.form['name']    
            
            # Check if the classroom already exists based on the name
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM classrooms WHERE name = %s", (name,))
            existing_classroom = cursor.fetchone()

            if existing_classroom:
                # Flash a message and re-render the form
                flash('Classroom already exists')
                return render_template('add_classrooms.html')  # Or you can redirect to the same page

            else:
                # Insert a new classroom
                cursor.execute("""
                    INSERT INTO classrooms (name)
                    VALUES (%s)
                """, (name,))

            mysql.connection.commit()

            return redirect(url_for('display_classrooms'))

        return render_template('add_classrooms.html')

    else:
        return redirect(url_for('login'))



@app.route('/add_classroomss', methods=['GET', 'POST'])
def add_classroomss():
    if request.method == 'POST':
        name = request.form['name']
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO classrooms (name)
            VALUES (%s)
        """, (name))
        mysql.connection.commit()
        cursor.close()
        
        flash('classroom added successfully')
        return redirect(url_for('add_classrooms'))
    return render_template('add_classrooms.html')

#########  ADD SUBJECTS  #############
@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if 'admin_id' in session:
        
        if request.method == 'POST':
            # Retrieve form data
            subject_id = request.form['subject_id']    
            
            # Check if the classroom already exists based on the name
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM subjects WHERE subject_id = %s", (subject_id,))
            existing_subject = cursor.fetchone()

            if existing_subject:
                # Flash a message and re-render the form
                flash('Subject already exists')
                return render_template('add_subject.html')  # Or you can redirect to the same page

            else:
                # Insert a new classroom
                cursor.execute("""
                    INSERT INTO subjects (subject_id)
                    VALUES (%s)
                """, (subject_id,))

            mysql.connection.commit()

            return redirect(url_for('display_subjects'))

        return render_template('add_subject.html')

    else:
        return redirect(url_for('login'))

###### EDIT SUBJECTS   ############
# Update
@app.route('/edit_subject/<subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if request.method == 'POST':
        new_subject_id = request.form['new_subject_id']
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE subjects 
            SET subject_id = %s 
            WHERE subject_id = %s
        """, (new_subject_id, subject_id))
        mysql.connection.commit()
        cursor.close()
        
        flash('Subject updated successfully')
        return redirect(url_for('display_subjects'))
    
    # GET request: fetch current subject data
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM subjects WHERE subject_id = %s", (subject_id,))
    subject = cursor.fetchone()
    cursor.close()
    
    if not subject:
        flash('Subject not found')
        return redirect(url_for('display_subjects'))
    
    return render_template('edit_subject.html', subject=subject)

# Delete subject
@app.route('/delete_subject/<subject_id>', methods=['POST'])
def delete_subject(subject_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM subjects WHERE subject_id = %s", (subject_id,))
    mysql.connection.commit()
    cursor.close()

    flash('Subject deleted successfully')
    return redirect(url_for('display_subjects'))

@app.route('/card')
def card():
    return render_template('card.html')

# PRINT HTML INTO PDF 
@app.route('/Test')
def Test():
    return render_template('Test.html')

# Generate pdf 
@app.route('/pdf')
def generate_pdf():
    rendered = render_template('display_pupils.html')
    pdf = pdfkit.from_string(rendered, False, configuration=config)
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
    
    return response

# Logout
@app.route('/logout')
def logout():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)