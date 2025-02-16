import os

class Config:
    # Database setup (adjust the URI for your own database setup)
    SQLALCHEMY_DATABASE_URI = 'oracle+cx_oracle://system:10012@localhost:1521/ORCL'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_secret_key')  # Use a secret key for JWT
    UPLOAD_FOLDER = './uploads'  # Specify folder for file uploads
