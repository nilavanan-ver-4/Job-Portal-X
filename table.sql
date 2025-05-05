-- table.sql
-- Create users table (job seekers)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    phone VARCHAR(15),
    age INTEGER CHECK (age >= 16 AND age <= 100),
    gender VARCHAR(20),
    address TEXT,
    highest_qualification VARCHAR(100),
    years_experience INTEGER CHECK (years_experience >= 0),
    skills TEXT,
    resume_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);


-- Create job_categories table
CREATE TABLE job_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    open_positions INTEGER CHECK (open_positions >= 0),
    experience_min INTEGER CHECK (experience_min >= 0),
    experience_max INTEGER CHECK (experience_max >= experience_min),
    icon_class VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create job_applications table
CREATE TABLE job_applications (
    id SERIAL PRIMARY KEY,
    job_title VARCHAR(100) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    age INTEGER CHECK (age >= 16 AND age <= 100),
    gender VARCHAR(20),
    address TEXT,
    highest_qualification VARCHAR(100),
    years_experience INTEGER CHECK (years_experience >= 0),
    skills TEXT,
    resume_url VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Under Review', 'Accepted', 'Rejected')),
    applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_application_per_job UNIQUE (job_title, user_id)
);

-- Create recruiters table (HR personnel)
CREATE TABLE recruiters (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Create trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to users table
CREATE TRIGGER update_users_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Apply trigger to job_applications table
CREATE TRIGGER update_applications_timestamp
BEFORE UPDATE ON job_applications
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Apply trigger to recruiters table
CREATE TRIGGER update_recruiters_timestamp
BEFORE UPDATE ON recruiters
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Apply trigger to job_categories table
CREATE TRIGGER update_categories_timestamp
BEFORE UPDATE ON job_categories
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Add hr_response and resume_updated_at columns to job_applications table
ALTER TABLE job_applications
ADD COLUMN hr_response TEXT,
ADD COLUMN resume_updated_at TIMESTAMP;

-- Insert a sample recruiter with a hashed password
INSERT INTO recruiters (username, full_name, email, password)
VALUES (
    'admin',
    'Admin Recruiter',
    'recruiter@example.com',
    '$2b$12$S4WJjLU6JIvGJaEz4T0Z4OP.RC/PSXZfaxGePY9gYGH3dDWy7ux.S' -- hashed password for 'admin'
);

-- Insert sample job categories from index.html
INSERT INTO job_categories (name, open_positions, experience_min, experience_max, icon_class) VALUES
    ('Design/Creative', 100, 2, 4, 'fas fa-paint-brush'),
    ('Programmer', 100, 1, 3, 'fas fa-code'),
    ('Data Scientist', 75, 2, 5, 'fas fa-database');