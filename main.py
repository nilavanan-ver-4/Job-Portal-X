from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2 import Error
import psycopg2.extras
from flask import send_from_directory
import os
import bcrypt

# Initialize Flask app
app = Flask(__name__, static_folder='templates/assets')
app.secret_key = 'your_secret_key'  # Replace with a secure key in production
CORS(app)

# PostgreSQL Configuration
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="job_platform",
            user="postgres",
            password="1234"  # Updated to match your PostgreSQL password
        )
        return conn
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

conn = get_db_connection()
if conn:
    print("Database connected successfully.")
    conn.close()
else:
    print("Failed to connect to the database.")

# Index route (Home page for sign-in/sign-up)
@app.route('/', methods=['GET'])
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, open_positions, experience_min, experience_max, icon_class FROM job_categories ORDER BY name")
        job_categories = [
            {
                'id': row[0],
                'name': row[1],
                'open_positions': row[2],
                'experience_min': row[3],
                'experience_max': row[4],
                'icon_class': row[5]
            } for row in cursor.fetchall()
        ]
        return render_template('index.html', job_categories=job_categories)
    except Error as e:
        print(f"Database Error: {e}")
        flash('An error occurred while loading job categories.', 'danger')
        return render_template('index.html', job_categories=[])
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT id, username, email, password FROM users WHERE email = %s OR username = %s",
                    (email_or_username, email_or_username)
                )
                user = cursor.fetchone()

                if user and check_password_hash(user[3], password):
                    session['user_id'] = user[0]
                    session['username'] = user[1]
                    session['email'] = user[2]
                    flash('Sign-in successful!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Invalid email/username or password.', 'danger')
                    return redirect(url_for('signin'))

            except Error as e:
                print(f"Database Error: {e}")
                flash('An error occurred while signing in.', 'danger')
                return redirect(url_for('signin'))
            finally:
                cursor.close()
                conn.close()
        else:
            flash('Database connection failed.', 'danger')
            return redirect(url_for('signin'))
    return render_template('account.html')

@app.route('/account')
def account():
    if 'username' in session:
        return render_template('account.html')
    flash('Please sign in to access your account.', 'warning')
    return redirect(url_for('signin'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('signin'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        flash('You must be signed in to view the dashboard.', 'warning')
        return redirect(url_for('signin'))

    try:
        conn = get_db_connection()
        if not conn:
            raise Error("Database connection failed.")

        cursor = conn.cursor()
        user_id = session['user_id']

        cursor.execute("""
            SELECT 
                job_title, full_name, email, phone, age, gender, address, 
                highest_qualification, years_experience, skills, resume_url, 
                status, applied_on, updated_at
            FROM 
                job_applications
            WHERE 
                user_id = %s
            ORDER BY 
                applied_on DESC
        """, (user_id,))

        applications = cursor.fetchall()
        applications_list = [
            {
                'job_title': app[0], 'full_name': app[1], 'email': app[2], 'phone': app[3],
                'age': app[4], 'gender': app[5], 'address': app[6], 'highest_qualification': app[7],
                'years_experience': app[8], 'skills': app[9], 'resume_url': app[10],
                'status': app[11], 'applied_on': app[12], 'updated_at': app[13]
            } for app in applications
        ]

        if not applications:
            flash('No job applications found.', 'info')

        return render_template('dashboard.jinja', applications=applications_list)

    except Error as e:
        print(f"Database Error: {e}")
        flash('An error occurred while loading the dashboard.', 'danger')
        return redirect(url_for('signin'))

    finally:
        if conn:
            cursor.close()
            conn.close()


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
        gender = request.form.get('gender')
        address = request.form.get('address')
        highest_qualification = request.form.get('highest_qualification')
        years_experience = request.form.get('years_experience')
        skills = request.form.get('skills')
        resume_url = request.form.get('resume_url')

        update_user_profile(
            username, email, phone, age, gender, address,
            highest_qualification, years_experience, skills, resume_url
        )
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('profile.html', user=user)

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, username, full_name, email, phone, age, gender, address, '
        'highest_qualification, years_experience, skills, resume_url '
        'FROM users WHERE username = %s',
        (username,)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return {
            'id': user[0], 'username': user[1], 'full_name': user[2], 'email': user[3],
            'phone': user[4], 'age': user[5], 'gender': user[6], 'address': user[7],
            'highest_qualification': user[8], 'years_experience': user[9], 'skills': user[10],
            'resume_url': user[11]
        }
    return None

def update_user_profile(username, email, phone, age, gender, address, highest_qualification,
                       years_experience, skills, resume_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE users
        SET email = %s, phone = %s, age = %s, gender = %s, address = %s,
            highest_qualification = %s, years_experience = %s, skills = %s, 
            resume_url = %s, updated_at = CURRENT_TIMESTAMP
        WHERE username = %s
        """,
        (email, phone, age, gender, address, highest_qualification,
         years_experience, skills, resume_url, username)
    )
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (username, full_name, email, password) "
                    "VALUES (%s, %s, %s, %s) RETURNING id",
                    (username, full_name, email, hashed_password)
                )
                user_id = cursor.fetchone()[0]
                conn.commit()
                flash('Account created successfully!', 'success')
                return redirect(url_for('signin'))
            except Error as e:
                conn.rollback()
                print(f"Database Error: {e}")
                flash(f'Error: {e}', 'danger')
                return redirect(url_for('signup'))
            finally:
                cursor.close()
                conn.close()
        else:
            flash('Database connection failed.', 'danger')
            return redirect(url_for('signup'))
    return render_template('account.html')

""" @app.route('/apply', methods=['POST'])
def apply():
    if 'user_id' not in session:
        flash('You must be signed in to apply for a job.', 'warning')
        return redirect(url_for('signin'))

    # Retrieve form data
    job_title = request.form.get('categoryName')  # Maps to job_title
    full_name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    age = request.form.get('age')
    gender = request.form.get('sex')  # Maps to gender
    address = request.form.get('address')
    highest_qualification = request.form.get('highest_qualification')
    years_experience = request.form.get('experience')  # Maps to years_experience
    skills = request.form.get('skills')
    resume_url = request.form.get('resume_url', '')  # Default to empty string if not provided
    user_id = session['user_id']

    # Basic form validation
    errors = []
    if not job_title or not full_name or not email or not phone or not age or not gender or not address or not highest_qualification or not years_experience or not skills:
        errors.append('All fields except Resume URL are required.')
    try:
        age = int(age)
        years_experience = int(years_experience)
        if age < 16 or age > 100:
            errors.append('Age must be between 16 and 100.')
        if years_experience < 0:
            errors.append('Years of experience cannot be negative.')
    except ValueError:
        errors.append('Age and years of experience must be valid numbers.')
    if gender not in ['M', 'F', 'O']:
        errors.append('Invalid gender selection.')

    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    query = ""
        INSERT INTO job_applications (
            job_title, user_id, full_name, email, phone, age, gender, address,
            highest_qualification, years_experience, skills, resume_url
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT unique_application_per_job
        DO NOTHING
    ""

    values = (
        job_title, user_id, full_name, email, phone, age, gender, address,
        highest_qualification, years_experience, skills, resume_url
    )

    try:
        cursor.execute(query, values)
        conn.commit()
        if cursor.rowcount > 0:
            flash('Application submitted successfully!', 'success')
            return redirect(url_for('thank_you'))
        else:
            flash('You have already applied for this job.', 'info')
            return redirect(url_for('dashboard'))
    except Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        flash('An error occurred while submitting the application.', 'danger')
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close() """
@app.route('/apply', methods=['POST'])
def apply():
    if 'user_id' not in session:
        flash('You must be signed in to apply for a job.', 'warning')
        return redirect(url_for('signin'))

    category_id = request.form.get('category_id')  # Updated to category_id
    full_name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    age = request.form.get('age')
    gender = request.form.get('sex')
    address = request.form.get('address')
    highest_qualification = request.form.get('highest_qualification')
    years_experience = request.form.get('experience')
    skills = request.form.get('skills')
    resume_url = request.form.get('resume_url', '')
    user_id = session['user_id']

    # Validate category_id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM job_categories WHERE id = %s", (category_id,))
    if not cursor.fetchone():
        flash('Invalid job category selected.', 'danger')
        return redirect(url_for('index'))

    # Rest of the validation and insertion logic remains the same, but use category_id
    query = """
        INSERT INTO job_applications (
            category_id, user_id, full_name, email, phone, age, gender, address,
            highest_qualification, years_experience, skills, resume_url
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT unique_application_per_category
        DO NOTHING
    """
    values = (
        category_id, user_id, full_name, email, phone, age, gender, address,
        highest_qualification, years_experience, skills, resume_url
    )
    # ... (rest of the logic remains the same)

@app.route('/job_categories', methods=['GET', 'POST'])
def job_categories():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')

        try:
            if action == 'add':
                name = request.form.get('name')
                open_positions = request.form.get('open_positions')
                experience_min = request.form.get('experience_min')
                experience_max = request.form.get('experience_max')
                icon_class = request.form.get('icon_class')

                # Validation
                errors = []
                if not name or len(name) > 100:
                    errors.append('Category name is required and must be less than 100 characters.')
                try:
                    open_positions = int(open_positions)
                    experience_min = int(experience_min)
                    experience_max = int(experience_max)
                    if open_positions < 0:
                        errors.append('Open positions must be non-negative.')
                    if experience_min < 0:
                        errors.append('Minimum experience must be non-negative.')
                    if experience_max < experience_min:
                        errors.append('Maximum experience must be greater than or equal to minimum experience.')
                except ValueError:
                    errors.append('Open positions, minimum experience, and maximum experience must be valid numbers.')
                if icon_class and len(icon_class) > 50:
                    errors.append('Icon class must be less than 50 characters.')

                if errors:
                    for error in errors:
                        flash(error, 'danger')
                else:
                    cursor.execute("""
                        INSERT INTO job_categories (name, open_positions, experience_min, experience_max, icon_class)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (name, open_positions, experience_min, experience_max, icon_class))
                    conn.commit()
                    flash('Job category added successfully!', 'success')

            elif action == 'edit':
                category_id = request.form.get('category_id')
                name = request.form.get('name')
                open_positions = request.form.get('open_positions')
                experience_min = request.form.get('experience_min')
                experience_max = request.form.get('experience_max')
                icon_class = request.form.get('icon_class')

                # Validation
                errors = []
                if not category_id or not name or len(name) > 100:
                    errors.append('Category ID and name are required, and name must be less than 100 characters.')
                try:
                    open_positions = int(open_positions)
                    experience_min = int(experience_min)
                    experience_max = int(experience_max)
                    if open_positions < 0:
                        errors.append('Open positions must be non-negative.')
                    if experience_min < 0:
                        errors.append('Minimum experience must be non-negative.')
                    if experience_max < experience_min:
                        errors.append('Maximum experience must be greater than or equal to minimum experience.')
                except ValueError:
                    errors.append('Open positions, minimum experience, and maximum experience must be valid numbers.')
                if icon_class and len(icon_class) > 50:
                    errors.append('Icon class must be less than 50 characters.')

                if errors:
                    for error in errors:
                        flash(error, 'danger')
                else:
                    cursor.execute("""
                        UPDATE job_categories 
                        SET name = %s, open_positions = %s, experience_min = %s, experience_max = %s, icon_class = %s
                        WHERE id = %s
                    """, (name, open_positions, experience_min, experience_max, icon_class, category_id))
                    conn.commit()
                    if cursor.rowcount > 0:
                        flash('Job category updated successfully!', 'success')
                    else:
                        flash('Job category not found.', 'danger')

            elif action == 'delete':
                category_id = request.form.get('category_id')
                try:
                    cursor.execute("DELETE FROM job_categories WHERE id = %s", (category_id,))
                    conn.commit()
                    if cursor.rowcount > 0:
                        flash('Job category deleted successfully!', 'success')
                    else:
                        flash('Job category not found.', 'danger')
                except psycopg2.errors.ForeignKeyViolation:
                    conn.rollback()
                    flash('Cannot delete this category because it is referenced by existing job applications.', 'danger')

        except Exception as e:
            conn.rollback()
            print(f"Database Error: {e}")
            flash('An error occurred while processing your request.', 'danger')

    # Fetch all job categories for display
    cursor.execute("SELECT id, name, open_positions, experience_min, experience_max, icon_class FROM job_categories ORDER BY name")
    categories = [
        {
            'id': row[0],
            'name': row[1],
            'open_positions': row[2],
            'experience_min': row[3],
            'experience_max': row[4],
            'icon_class': row[5]
        } for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()
    return render_template('job_categories.html', categories=categories)


@app.route('/hr_portal', methods=['GET'])
def hr_portal():
    if 'recruiter_username' not in session:
        flash('You must be signed in to access the Recruiter Portal.', 'warning')
        return redirect(url_for('hr_signin'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                id, job_title, full_name, email, phone, age, gender, address, 
                highest_qualification, years_experience, skills, resume_url,
                status, applied_on, updated_at
            FROM 
                job_applications
            ORDER BY 
                job_title, applied_on DESC
        """)

        applications = cursor.fetchall()
        grouped_applications = {}
        for app in applications:
            job_title = app[1]
            if job_title not in grouped_applications:
                grouped_applications[job_title] = []
            grouped_applications[job_title].append({
                'id': app[0], 'job_title': app[1], 'full_name': app[2], 'email': app[3],
                'phone': app[4], 'age': app[5], 'gender': app[6], 'address': app[7],
                'highest_qualification': app[8], 'years_experience': app[9], 'skills': app[10],
                'resume_url': app[11], 'status': app[12], 'applied_on': app[13], 'updated_at': app[14]
            })

        return render_template('hr_portal.jinja', grouped_applications=grouped_applications)

    except Error as e:
        print(f"Database Error: {e}")
        flash('An error occurred while loading the Recruiter Portal.', 'danger')
        return redirect(url_for('hr_signin'))

    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/update_application_status', methods=['POST'])
def update_application_status():
    if 'recruiter_username' not in session:
        flash('You must be signed in to update application status.', 'warning')
        return redirect(url_for('hr_signin'))

    application_id = request.form.get('application_id')
    new_status = request.form.get('status')

    if new_status not in ['Pending', 'Under Review', 'Accepted', 'Rejected']:
        flash('Invalid status value.', 'danger')
        return redirect(url_for('hr_portal'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE job_applications
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (new_status, application_id)
        )
        conn.commit()
        flash('Application status updated successfully!', 'success')
    except Error as e:
        print(f"Database Error: {e}")
        flash('An error occurred while updating the status.', 'danger')
    finally:
        if conn:
            cursor.close()
            conn.close()

    return redirect(url_for('hr_portal'))


@app.route('/hr_signin', methods=['GET', 'POST'])
def hr_signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        conn = None
        cursor = None

        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            cursor.execute(
                "SELECT username, password FROM recruiters WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
                session['recruiter_username'] = user['username']
                flash('Sign-In successful!', 'success')
                return redirect(url_for('hr_portal'))
            else:
                flash('Invalid username or password.', 'danger')

        except Error as e:
            print(f"Database Error: {e}")
            flash('An error occurred during sign-in.', 'danger')

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('hr_signin.jinja')


@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True)