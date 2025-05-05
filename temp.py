import bcrypt

# Plain-text password to hash
plain_password = b'1234'  # Example password

# Hash the password with bcrypt
hashed_password = bcrypt.hashpw(plain_password, bcrypt.gensalt())

# You would insert `hashed_password` into the database instead of plain-text password
print(hashed_password.decode())  # Print the hashed password to see how it looks
