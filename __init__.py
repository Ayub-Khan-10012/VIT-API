from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate  # Import Migrate

# Initialize Flask app
app = Flask(__name__)

# Database Configuration (Update for your Oracle DB)
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle+cx_oracle://system:10012@localhost:1521/XE'  # Update to correct URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a secure key
app.config['UPLOAD_FOLDER'] = './uploads'  # Specify folder for file uploads

# Initialize Database, JWT Manager, and Migrate
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Import routes after app initialization to avoid circular imports
from app import routes
