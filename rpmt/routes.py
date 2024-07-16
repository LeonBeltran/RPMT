from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from rpmt import app, db, bcrypt
from rpmt.forms import LoginForm, ProjectForm
from rpmt.models import User, Project, Author, Editor, AuthorProject, EditorProject

from _scratch.dummydata import dummy_data

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
    if current_user.is_authenticated:
        flash(f'Already logged in as {current_user.username}', 'warning')
        return redirect(url_for('home'))
    form = LoginForm()
    return render_template("login.html", form=form)
@app.post("/login")
def login_post():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Logged in as {user.username}', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful, please check your credentials. Contact the site administrators if you believe something is wrong.', 'danger')
    return render_template("login.html", form=form)

# Logout
# ----------------------------------------------------------------------------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash(f'Logged out successfully', 'success')
    return redirect(url_for('home'))

# Admin: Admin Area
# ----------------------------------------------------------------------------------------------
@app.get("/admin/")
@login_required
def admin():
    return render_template("admin.html")

# Admin: Generate Projects Report
# ----------------------------------------------------------------------------------------------
@app.get("/admin/report")
@login_required
def report():
    return render_template("report.html")

# Admin: Adding Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/add")
@login_required
def add_project():
    form = ProjectForm()
    return render_template("projectform.html", form=form)
@app.post("/admin/add")
@login_required
def add_project_post():
    form = ProjectForm()
    if form.validate_on_submit():
        try:
            new_project = Project(
                creator_id=current_user.id,
                title=form.title.data,
                abstract=form.abstract.data or "No abstract provided",
                type=form.type.data,
                date_published=form.date_published.data,
                publicaiton_name=form.publication_name.data,
                publisher=form.publisher.data,
                publisher_type=form.publisher_type.data,
                publisher_location=form.publisher_location.data,
                vol_issue_no=form.vol_issue_no.data,
                doi_url=form.doi_url.data,
                isbn_issn=form.isbn_issn.data,
                web_of_science=form.web_of_science.data,
                elsevier_scopus=form.elsevier_scopus.data,
                elsevier_sciencedirect=form.elsevier_sciencedirect.data,
                pubmed_medline=form.pubmed_medline.data,
                ched_recognized=form.ched_recognized.data,
                other_database=form.other_database.data,
                citations=form.citations.data,
                publication_proof=form.publication_proof.data if form.publication_proof.data else "none.png",
                utilization_proof=form.utilization_proof.data if form.utilization_proof.data else "none.png"
            )
            db.session.add(new_project)
            db.session.commit()
            
            authors_data = form.authors.data.split(', ')
            for author_name in authors_data:
                author = Author.query.filter_by(name=author_name).first()
                if not author:
                    author = Author(name=author_name)
                    db.session.add(author)
                    db.session.commit()
                author_project = AuthorProject(author_id=author.id, project_id=new_project.id)
                db.session.add(author_project)
                
            editors_data = form.editors.data.split(', ')
            for editor_name in editors_data:
                editor = Editor.query.filter_by(name=editor_name).first()
                if not editor:
                    editor = Editor(name=editor_name)
                    db.session.add(editor)
                    db.session.commit()
                editor_project = EditorProject(editor_id=editor.id, project_id=new_project.id)
                db.session.add(editor_project)
            
            db.session.commit()
        
            flash('Project created successfully', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', 'danger')
    else:
        flash('Project creation failed, please try again', 'danger')
    return render_template("projectform.html", form=form)

# Admin: Deleting Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/delete/")
@login_required
def delete_project_list():
    return render_template("projectlist.html", data=dummy_data, mode="Delete")

@app.get("/admin/delete/<int:paper_id>")
@login_required
def delete_project(paper_id):
    data = [dummy_data[paper_id]]
    return render_template("projectlist.html", data=data, mode="Deleted")

# Admin: Editing Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/edit/")
@login_required
def edit_project_list():
    return render_template("projectlist.html", data=dummy_data, mode="Edit")

@app.get("/admin/edit/<int:paper_id>")
@login_required
def edit_project(paper_id):
    mode = "Editing " + dummy_data[paper_id]["Name"]
    return render_template("projectform.html", mode=mode)
@app.post("/admin/edit/<int:paper_id>")
@login_required
def edit_project_post(paper_id):
    mode = "Edited " + dummy_data[paper_id]["Name"]
    return render_template("projectform.html", mode=mode)