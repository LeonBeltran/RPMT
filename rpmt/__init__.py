from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

from rpmt import routes