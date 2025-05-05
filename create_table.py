import psycopg2
from psycopg2 import Error

def create_database(dbname, user, password, host="localhost"):
    """
    Create the specified database if it doesn't exist.
    """
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host
        )
        conn.set_session(autocommit=True)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {dbname}")
            print(f"Database '{dbname}' created successfully.")
        else:
            print(f"Database '{dbname}' already exists.")

        return True
    except Error as e:
        print(f"Error creating database '{dbname}': {e}")
        print("Ensure the PostgreSQL server is running and credentials are correct.")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def check_tables(dbname, user, password, host="localhost", expected_tables=None):
    """
    Check if the expected tables exist in the database.
    
    Parameters:
    - expected_tables: List of table names to check (e.g., ['users', 'job_applications', 'recruiters'])
    """
    if expected_tables is None:
        expected_tables = ['users', 'job_applications', 'recruiters']
    
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [table for table in expected_tables if table not in existing_tables]
        if not missing_tables:
            print(f"All expected tables {expected_tables} exist in '{dbname}' database.")
            return True
        else:
            print(f"Missing tables in '{dbname}': {missing_tables}")
            return False
    except Error as e:
        print(f"Error checking tables in '{dbname}': {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def run_sql_file(filename, dbname, user, password, host="localhost"):
    """
    Execute a .sql file to set up tables in the specified database.
    """
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        conn.set_session(autocommit=True)
        cursor = conn.cursor()

        with open(filename, 'r') as file:
            sql_commands = file.read()

        cursor.execute(sql_commands)
        print(f"Successfully executed {filename}")
        print(f"Tables 'users', 'job_applications', 'recruiters' created in '{dbname}' database.")
        return True
    except Error as e:
        print(f"Error executing {filename}: {e}")
        print(f"Ensure the '{dbname}' database exists and the SQL syntax is correct.")
        return False
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def verify_connection(dbname, user, password, host="localhost"):
    """
    Verify connection to the database and list tables.
    """
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        print(f"Connection to '{dbname}' database successful. Tables found:", [table[0] for table in tables])
    except Error as e:
        print(f"Error connecting to '{dbname}' database: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def check_job_applications_columns(dbname, user, password, host="localhost"):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'job_applications' 
            AND column_name IN ('hr_response', 'resume_updated_at')
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Columns found in job_applications: {columns}")
        return len(columns) == 2
    except Error as e:
        print(f"Error checking columns: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Execute
#check_job_applications_columns("job_platform", "postgres", "1234")  # Updated to match your new PostgreSQL password

if __name__ == "__main__":
    sql_file = "table.sql"
    dbname = "job_platform"
    user = "postgres"
    password = "1234"  # Updated to match your new PostgreSQL password

    # Create the database (or confirm it exists)
    if create_database(dbname, user, password):
        # Check if tables exist
        if check_tables(dbname, user, password):
            print("No need to run table.sql; all tables already exist.")
        else:
            # Run the SQL file to create tables
            if run_sql_file(sql_file, dbname, user, password):
                # Verify the connection and tables
                verify_connection(dbname, user, password)
    else:
        print("Failed to create or access the database. Please check PostgreSQL setup.")