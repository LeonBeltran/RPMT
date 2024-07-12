from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from dotenv import load_dotenv
import os

# Setup
# ----------------------------------------------------------------------------------------------
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Database
# ----------------------------------------------------------------------------------------------
# Local file method
# Stored in instance/data.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Authentication
# ----------------------------------------------------------------------------------------------
bcrypt = Bcrypt(app)

from rpmt import routes