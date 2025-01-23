from flask import Flask, render_template, request, redirect, url_for, flash,jsonify,session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from flask import send_from_directory
import os
import bcrypt



# Initialize Flask app
app = Flask(__name__, static_folder='templates/assets')
app.secret_key = 'your_secret_key'
CORS(app)

# MySQL Configuration
def get_db_connection():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="users"
        )
        return db
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

db = get_db_connection()
if db:
    print("Database connected successfully.")
else:
    print("Failed to connect to the database.")

cursor = db.cursor()

""" # Configure file upload settings
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) """




# Index route (Home page for sign-in/sign-up)
@app.route('/')
def index():
    return render_template('index.jinja')  # Points to your combined Sign-In/Sign-Up page
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']

        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            try:
                # Query to check if the input matches either an email or a username
                cursor.execute("SELECT username, email, password FROM user_1 WHERE email = %s OR username = %s",
                               (email_or_username, email_or_username))
                user = cursor.fetchone()

                if user and check_password_hash(user['password'], password):
                    # If valid, store the username and email in the session
                    session['username'] = user['username']
                    session['email'] = user['email']
                    flash('Sign-in successful!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Invalid email/username or password. Please try again.', 'danger')
                    return redirect(url_for('signin'))

            except mysql.connector.Error as err:
                print(f"Database Error: {err}")
                flash('An error occurred while signing in. Please try again later.', 'danger')
                return redirect(url_for('signin'))
        else:
            print("Database connection failed.")
            flash('Database connection failed.', 'danger')
            return redirect(url_for('signin'))
    else:
        return render_template('account.html')  # Render the sign-in form on GET request
    
@app.route('/account')
def account():
    if 'username' in session:
        return render_template('account.html')  # Replace with your actual account page
    else:
        flash('Please sign in to access your account.', 'warning')
        return redirect(url_for('signin'))
@app.route('/logout')
def logout():
    # Clear session data
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('signin'))  # Redirect to the sign-in page


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'username' not in session:
        flash('You must be signed in to view the dashboard.', 'warning')
        return redirect(url_for('signin'))

    try:
        db = get_db_connection()
        if not db:
            raise mysql.connector.Error("Database connection failed.")
        
        cursor = db.cursor(dictionary=True)
        
        # Fetch the email of the logged-in user from the session
        user_email = session.get('email')
        if not user_email:
            flash('User email not found in session.', 'warning')
            return redirect(url_for('signin'))
        
        # Query to fetch job applications with matching emails
        cursor.execute("""
            SELECT 
                j.category_name, j.name, j.email, j.phone, j.age, j.sex, j.address, 
                j.highest_qualification, j.experience, j.skills, j.applied_on
            FROM 
                job_applications j
            INNER JOIN 
                user_1 u ON j.email = u.email
            WHERE 
                u.email = %s
            ORDER BY 
                j.applied_on DESC
        """, (user_email,))
        
        applications = cursor.fetchall()
        
        if not applications:
            flash('No job applications found for your account.', 'info')
        
        return render_template('dashboard.jinja', applications=applications)
    
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('An error occurred while loading the dashboard.', 'danger')
        return redirect(url_for('signin'))
    
    finally:
        if db.is_connected():
            db.close()



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        flash('You must be signed in to access your profile.', 'warning')
        return redirect(url_for('signin'))

    username = session['username']
    user = get_user_by_username(username)

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('signin'))

    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')
        sex = request.form.get('sex')
        address = request.form.get('address')
        highest_qualification = request.form.get('highest_qualification')
        experience = request.form.get('experience')
        skills = request.form.get('skills')

        update_user_profile(username, email, phone, age, sex, address, highest_qualification, experience, skills)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('profile.html', user=user)

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM user_1 WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def update_user_profile(username, email, phone, age, sex, address, highest_qualification, experience, skills):
    conn = get_db_connection()
    cursor = conn.cursor()
    update_query = """
        UPDATE user_1
        SET email = %s, phone = %s, age = %s, sex = %s, address = %s, highest_qualification = %s, experience = %s, skills = %s
        WHERE username = %s
    """
    cursor.execute(update_query, (email, phone, age, sex, address, highest_qualification, experience, skills, username))
    conn.commit()
    cursor.close()
    conn.close()




# Sign-up route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Debug print statements
        print(f"Received data: username={username}, email={email}, password={password}, confirm_password={confirm_password}")

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        print(f"Hashed password: {hashed_password}")

        db = get_db_connection()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute("INSERT INTO user_1(username,name, email, password) VALUES (%s, %s, %s, %s)",
                               (username,name, email, hashed_password))
                db.commit()
                print("Account successfully created.")
                flash('Account successfully created!', 'success')
                return redirect(url_for('signin'))  # Redirect to the sign-in page after successful registration
            except mysql.connector.Error as err:
                db.rollback()
                print(f"Database Error: {err}")
                flash(f'Error: {err}', 'danger')
                return redirect(url_for('signup'))
        else:
            print("Database connection failed.")
            flash('Database connection failed.', 'danger')
            return redirect(url_for('signup'))
    else:
        return render_template('account.html')  # Render the sign-up form on GET request


@app.route('/apply', methods=['POST'])
def apply():
    if request.method == 'POST':

        print("Form data received:", request.form)

        category_name = request.form.get('categoryName')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')
        sex = request.form.get('sex')
        address = request.form.get('address')
        highest_qualification = request.form.get('highest_qualification')
        experience = request.form.get('experience')
        skills = request.form.get('skills')

        print("Category Name:", category_name)
        print("Name:", name)
        print("Email:", email)

        print(f"Received data: {category_name}, {name}, {email}, {phone}, {age}, {sex}, {address}, {highest_qualification}, {experience}, {skills}")

        


        # Insert data into the database
        query = """
    INSERT INTO job_applications (category_name, name, email, phone, age, sex, address, highest_qualification, 
                                   experience, skills)
    SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    WHERE NOT EXISTS (
        SELECT 1 
        FROM job_applications 
        WHERE category_name = %s AND email = %s
    )
"""

        values = (category_name, name, email, phone, age, sex, address, highest_qualification, experience, skills)

        print("Category Name:", category_name)
        print("Name:", name)
        print("Email:", email)


        try:
            cursor.execute(query, values)
            db.commit()
            if cursor.rowcount > 0:
                flash('Application submitted successfully!', 'success')
            else:
                flash('Application already exists for this category and email.', 'info')

            return redirect(url_for('dashboard'))
        except mysql.connector.Error as err:
            db.rollback()
            print(f"Database error: {err}")
            flash('An error occurred while submitting the application. Please try again.', 'danger')
            return redirect(url_for('thank_you'))

""" @app.route('/hr_portal', methods=['POST'])
def hr_portal():
    if 'username' not in session:
        flash('You must be signed in to access the HR Portal.', 'warning')
        return redirect(url_for('hr_signin'))

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Fetch all applications grouped by category_name
        cursor.execute(""
            SELECT 
                category_name, name, email, phone, age, sex, address, 
                highest_qualification, experience, skills, applied_on
            FROM 
                job_applications
            ORDER BY 
                category_name, applied_on DESC
        "")
        
        applications = cursor.fetchall()

        # Group applications by category_name
        grouped_applications = {}
        for app in applications:
            category = app['category_name']
            if category not in grouped_applications:
                grouped_applications[category] = []
            grouped_applications[category].append(app)
        
        return render_template('hr_portal.jinja', grouped_applications=grouped_applications)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('An error occurred while loading the HR Portal.', 'danger')
        return redirect(url_for('hr_signin'))

    finally:
        if db.is_connected():
            db.close() """
@app.route('/hr_portal', methods=['GET'])
def hr_portal():
    if 'username' not in session:
        flash('You must be signed in to access the HR Portal.', 'warning')
        return redirect(url_for('hr_signin'))

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Fetch all applications grouped by category_name
        cursor.execute("""
            SELECT 
                category_name, name, email, phone, age, sex, address, 
                highest_qualification, experience, skills, applied_on
            FROM 
                job_applications
            ORDER BY 
                category_name, applied_on DESC
        """)
        
        applications = cursor.fetchall()

        # Group applications by category_name
        grouped_applications = {}
        for app in applications:
            category = app['category_name']
            if category not in grouped_applications:
                grouped_applications[category] = []
            grouped_applications[category].append(app)
        
        return render_template('hr_portal.jinja', grouped_applications=grouped_applications)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('An error occurred while loading the HR Portal.', 'danger')
        return redirect(url_for('hr_signin'))

    finally:
        if 'db' in locals() and db.is_connected():
            db.close()

@app.route('/hr_signin', methods=['GET', 'POST'])
def hr_signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            # Query to validate HR credentials
            cursor.execute("""
                SELECT username, password FROM hr_users WHERE username = %s
            """, (username,))
            user = cursor.fetchone()

            if user and password == user['password']:  # Simple password check (use with caution)
                # Store user information in the session
                session['username'] = user['username']
                flash('Sign-In successful!', 'success')
                return redirect(url_for('hr_portal'))
            else:
                flash('Invalid username or password.', 'danger')

        except mysql.connector.Error as err:
            print(f"Database Error: {err}")
            flash('An error occurred during sign-in.', 'danger')

        finally:
            if 'db' in locals() and db.is_connected():
                db.close()
    
    # If GET request or POST fails, render the sign-in template
    return render_template('hr_signin.jinja')


@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

""" def allowed_file(filename):
    allowed_extensions = {'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions """


if __name__ == '__main__':
    app.run(debug=True)
