from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path
import sys
import os

# Setup
# ----------------------------------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
else:
    base_path = Path(__file__).parent
dotenv_path = base_path / '.env'
load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Supabase
# ----------------------------------------------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Database
# ----------------------------------------------------------------------------------------------
# Where the database file is located
# Can be online to have online syncing
# Local: "sqlite:///" + str(os.path.join(base_path, 'db.sqlite3'))
DATABASE_URI = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Authentication
# ----------------------------------------------------------------------------------------------
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Supabase Functions
# ----------------------------------------------------------------------------------------------
def upload_file(filename, f):
    try:
        _, ext = os.path.splitext(filename)
        supabase.storage.from_('RPMT').upload(file=f.read(), path=filename, file_options={"content-type": ext[1:]})
    except Exception as e:
        print(f"Error uploading file: {str(e)}")

def delete_file(filename):
    try:
        supabase.storage.from_('RPMT').remove([filename])
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        
def get_file_url(filename):
    try:
        return supabase.storage.from_('RPMT').get_public_url(filename)
    except:
        print(f"Error deleting file: {str(e)}")

from rpmt import routes