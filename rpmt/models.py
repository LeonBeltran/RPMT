from rpmt import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
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
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', name='fk_author_project_id', ondelete='CASCADE'), nullable=False)
    
class EditorProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    editor_id = db.Column(db.Integer, db.ForeignKey('editor.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', name='fk_editor_project_id', ondelete='CASCADE'), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    authors = db.relationship('AuthorProject', backref='project', lazy=True, cascade="all, delete")
    abstract = db.Column(db.String(512), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    date_published = db.Column(db.Date, nullable=False)
    publication_name = db.Column(db.String(128), nullable=False)
    publisher = db.Column(db.String(64), nullable=False)
    publisher_type = db.Column(db.String(32), nullable=False)
    publisher_location = db.Column(db.String(16), nullable=False)
    editors = db.relationship('EditorProject', backref='project', lazy=True, cascade="all, delete")
    vol_issue_no = db.Column(db.Integer, nullable=False)
    doi_url = db.Column(db.String(256), unique=True, nullable=False)
    isbn_issn = db.Column(db.String(4), nullable=False)
    web_of_science = db.Column(db.Boolean, nullable=False)
    elsevier_scopus = db.Column(db.Boolean, nullable=False)
    elsevier_sciencedirect = db.Column(db.Boolean, nullable=False)
    pubmed_medline = db.Column(db.Boolean, nullable=False)
    ched_recognized = db.Column(db.Boolean, nullable=False)
    other_database = db.Column(db.String(128), nullable=False)
    publication_proof = db.Column(db.String(32), nullable=False)
    citations = db.Column(db.Integer, nullable=False)
    utilization_proof = db.Column(db.String(32), nullable=False)
    
    def __repr__(self):
        return f"Project {self.id}: {self.title}"