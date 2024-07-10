from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

from Scratch.dummydata import dummy_data

# Setup
# ----------------------------------------------------------------------------------------------
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Database
# ----------------------------------------------------------------------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(8), nullable=False)
    projects = db.relationship('Project', backref='creator', lazy=True)
    
    def __repr__(self):
        return f"User {self.id}: {self.username} | {self.email}"
    
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    projects = db.relationship('AuthorProject', backref='author', lazy=True)
    
    def __repr__(self):
        return f"Author {self.id}: {self.name}"

class Editor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    projects = db.relationship('EditorProject', backref='editor', lazy=True)
    
    def __repr__(self):
        return f"Editor {self.id}: {self.name}"
    
class AuthorProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
class EditorProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('editor.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    authors = db.relationship('AuthorProject', backref='project', lazy=True)
    abstract = db.Column(db.String(512), nullable=True)
    type = db.Column(db.String(64), nullable=False)
    date_published = db.Column(db.Date, nullable=False)
    publication_name = db.Column(db.String(128), nullable=False)
    publisher = db.Column(db.String(64), nullable=False)
    publisher_type = db.Column(db.String(32), nullable=False)
    publisher_location = db.Column(db.String(16), nullable=False)
    editors = db.relationship('EditorProject', backref='project', lazy=True)
    vol_issue_no = db.Column(db.Integer, nullable=False)
    doi_url = db.Column(db.String(256), unique=True, nullable=False)
    isbn_issn = db.Column(db.String(4), nullable=False)
    web_of_science = db.Column(db.Boolean, nullable=False)
    elsevier_scopus = db.Column(db.Boolean, nullable=False)
    elsevier_sciencedirect = db.Column(db.Boolean, nullable=False)
    pubmed_medline = db.Column(db.Boolean, nullable=False)
    ched_recognized = db.Column(db.Boolean, nullable=False)
    other_database = db.Column(db.String(128), nullable=False)
    publication_proof = db.Column(db.String(32), nullable=False, default='none.png')
    citations = db.Column(db.Integer, nullable=False)
    utilization_proof = db.Column(db.String(32), nullable=False, default='none.png')
    
    def __repr__(self):
        return f"Project {self.id}: {self.title}"

# Home Page
# ----------------------------------------------------------------------------------------------
@app.get("/")
@app.get("/home")
def home():
    return render_template("home.html")

# Projects Page
# ----------------------------------------------------------------------------------------------

@app.get("/projects/")
def project_list():
    return render_template("projectlist.html", data=dummy_data, mode="View")
@app.get("/projects/<int:paper_id>")
def project_page(paper_id):
    return render_template("projectpage.html", project=dummy_data[paper_id])

# Admin: Login Page
# ----------------------------------------------------------------------------------------------
@app.get("/login")
def login():
    return render_template("login.html")
@app.post("/login")
def login_post():
    return render_template("login.html")

# Admin: Admin Area
# ----------------------------------------------------------------------------------------------
@app.get("/admin/")
def admin():
    return render_template("admin.html")

# Admin: Generate Projects Report
# ----------------------------------------------------------------------------------------------
@app.get("/admin/report")
def report():
    return render_template("report.html")

# Admin: Adding Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/add")
def add_project():
    return render_template("projectform.html")

@app.post("/admin/add")
def add_project_post():
    return render_template("projectform.html")

# Admin: Deleting Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/delete/")
def delete_project_list():
    return render_template("projectlist.html", data=dummy_data, mode="Delete")

@app.get("/admin/delete/<int:paper_id>")
def delete_project(paper_id):
    data = [dummy_data[paper_id]]
    return render_template("projectlist.html", data=data, mode="Deleted")

# Admin: Editing Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/edit/")
def edit_project_list():
    return render_template("projectlist.html", data=dummy_data, mode="Edit")

@app.get("/admin/edit/<int:paper_id>")
def edit_project(paper_id):
    mode = "Editing " + dummy_data[paper_id]["Name"]
    return render_template("projectform.html", mode=mode)
@app.post("/admin/edit/<int:paper_id>")
def edit_project_post(paper_id):
    mode = "Edited " + dummy_data[paper_id]["Name"]
    return render_template("projectform.html", mode=mode)

if __name__ == '__main__':
    app.run(debug=True)