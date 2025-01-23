# Job Portal Web Application

## Overview
A full-featured job application and HR management web application built with Flask and MySQL, designed to facilitate job applications and streamline HR processes.

## Technologies Used
- **Backend**: Flask (Python)
- **Database**: MySQL
- **Authentication**: Flask-Session, Werkzeug Security
- **Frontend**: Jinja2 Templates

## Project Structure
```
job-portal/
├── app.py                  # Main Flask application
├── templates/              # HTML templates
│   ├── index.jinja
│   ├── account.html
│   ├── dashboard.jinja
│   ├── profile.html
│   └── hr_portal.jinja
├── Dockerfile              # Docker configuration
└── requirements.txt        # Python dependencies
```

## Features
- User Authentication
  - Sign Up
  - Sign In
  - Logout
- User Dashboard
- Job Application Submission
- HR Portal
- Profile Management

## Database Schema
### Users Table (`user_1`)
- username
- name
- email
- password (hashed)
- phone
- age
- sex
- address
- highest_qualification
- experience
- skills

### Job Applications Table (`job_applications`)
- category_name
- name
- email
- phone
- age
- sex
- address
- highest_qualification
- experience
- skills
- applied_on

## Docker Setup

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### requirements.txt
```
flask
flask-cors
mysql-connector-python
werkzeug
bcrypt
```

## Environment Setup

1. Clone the Repository
```bash
git clone https://github.com/yourusername/job-portal.git
cd job-portal
```

2. MySQL Database Setup
```sql
CREATE DATABASE users;
USE users;

CREATE TABLE user_1 (
    username VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    phone VARCHAR(20),
    age INT,
    sex VARCHAR(10),
    address TEXT,
    highest_qualification VARCHAR(100),
    experience VARCHAR(100),
    skills TEXT
);

CREATE TABLE job_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100),
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    age INT,
    sex VARCHAR(10),
    address TEXT,
    highest_qualification VARCHAR(100),
    experience VARCHAR(100),
    skills TEXT,
    applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

3. Docker Deployment
```bash
docker build -t job-portal .
docker run -p 5000:5000 job-portal
```

## Security Considerations
- Password hashing with Werkzeug
- Session-based authentication
- Input validation
- Database connection error handling

## Future Improvements
- Implement more robust password reset
- Add email verification
- Enhance HR portal with advanced filtering
- Implement role-based access control

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request


## Troubleshooting
- Ensure MySQL service is running
- Check database connection parameters
- Verify Python and pip installations

## License
This project is licensed under the MIT License - see the [MIT](LICENSE) file for details.
