from multiprocessing import connection
from sqlite3 import Cursor
from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb.cursors
import re 
import yaml

#cursor = connection.cursor()
app = Flask(__name__,static_folder='./static',static_url_path='/static')
#Set secret key for the session
app.secret_key = "super secret key"

#Configure my sql db details
db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

# Instantiation of MySQL Object
mysql = MySQL(app)

#End Point -
@app.route('/',methods=['GET', 'POST'])
def login():
    global UserId
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM testdb.accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            #session['id'] = account['username']
            #session['name'] = account['username']
            session['id'] = account['id']
            session['username'] = account['username']
            #UserId = account['username']
            
            # Redirect to home page
            msg = 'Logged in successfully!'
            #return redirect(url_for('home'))
            return render_template('home.html', msg = msg)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            flash("Incorrect username/password!", "danger")
    # Show the login form with message (if any)
    return render_template('index.html', msg = msg)

#End Point - Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

#End Point - Home Page
@app.route('/home')
def home():
    #return render_template('home.html', username = session['username'])
    return render_template('home.html')

#End Point - To display all the Course Details
@app.route('/course_list')
def course_list():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from course")
    if resultValue > 0:
        courseSelectDetails = cur.fetchall()
        return render_template('course_list.html',courseSelectDetails=courseSelectDetails)

#End Point - Update the Course table in MySQL Database
@app.route('/update_course', methods=['GET','POST'])
def update_course():
    if request.method == 'POST':
    # Fetch form data
        updateCourseDetails = request.form
        course_id = updateCourseDetails['course_id']
        credit_hours = updateCourseDetails['credit_hours']
        course_name = updateCourseDetails['course_name']
        cur = mysql.connection.cursor()      
        cur.execute("INSERT INTO course (course_id, credit_hours, course_name) VALUES (%s, %s, %s)",(course_id, credit_hours, course_name))
        mysql.connection.commit()
        cur.close()
        return redirect('/course_list')
    else:
        return render_template('update_course.html')

#End Point - Delete the Course table in MySQL Database
@app.route('/delete_course', methods=['GET','POST'])
def delete_course():
    if request.method == 'POST':
    # Fetch form data
        deleteCourseDetails = request.form
        course_id = deleteCourseDetails['course_id']
        credit_hours = deleteCourseDetails['credit_hours']
        #course_name = deleteCourseDetails['course_name']
        cur = mysql.connection.cursor()      
        cur.execute("DELETE FROM course WHERE course_id = %s AND credit_hours = %s", (course_id, credit_hours))
        mysql.connection.commit()
        cur.close()
        return redirect('/course_list')
    else:
        return render_template('delete_course.html')


#This will ensure that any changes made updated immediately on the web browser
if __name__ == '__main__':
  app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0')    