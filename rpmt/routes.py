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
    projects = Project.query.all()
    return render_template("projectlist.html", data=projects, mode="View")
@app.get("/projects/<int:paper_id>")
def project_page(paper_id):
    project = Project.query.filter_by(id=paper_id)
    return render_template("projectpage.html", project=project)

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
    mode = "Adding a New Project"
    form = ProjectForm()
    return render_template("projectform.html", form=form, mode=mode)
@app.post("/admin/add")
@login_required
def add_project_post():
    mode = "Adding a New Project"
    form = ProjectForm()
    if form.validate_on_submit():
        try:
            new_project = Project(
                creator_id=current_user.id,
                title=form.title.data,
                abstract=form.abstract.data or "No abstract provided",
                type=form.type.data,
                date_published=form.date_published.data,
                publication_name=form.publication_name.data,
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
    return render_template("projectform.html", form=form, mode=mode)

# Admin: Deleting Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/delete/")
@login_required
def delete_project_list():
    projects = Project.query.all()
    return render_template("projectlist.html", data=projects, mode="Delete")

@app.get("/admin/delete/<int:paper_id>")
@login_required
def delete_project(paper_id):
    to_delete = Project.query.filter_by(id=paper_id).first()
    db.session.delete(to_delete)
    db.session.commit()
    flash('Successfully deleted project', 'success')
    return redirect(url_for('admin'))

# Admin: Editing Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/edit/")
@login_required
def edit_project_list():
    projects = Project.query.all()
    return render_template("projectlist.html", data=projects, mode="Edit")

@app.get("/admin/edit/<int:paper_id>")
@login_required
def edit_project(paper_id):
    project = Project.query.filter_by(id=paper_id).first()
    mode = "Editing " + project.title
    
    authors_data = ', '.join([ap.author.name for ap in project.authors])
    editors_data = ', '.join([ep.editor.name for ep in project.editors])
    
    form = ProjectForm(obj=project)
    form.authors.data = authors_data
    form.editors.data = editors_data

    return render_template("projectform.html", mode=mode, form=form)
@app.post("/admin/edit/<int:paper_id>")
@login_required
def edit_project_post(paper_id):
    project = Project.query.filter_by(id=paper_id).first()
    mode = "Editing " + project.title
    form = ProjectForm()
    if form.validate_on_submit():
        try:
            project.title = form.title.data
            project.abstract = form.abstract.data or "No abstract provided"
            project.type = form.type.data
            project.date_published = form.date_published.data
            project.publication_name = form.publication_name.data
            project.publisher = form.publisher.data
            project.publisher_type = form.publisher_type.data
            project.publisher_location = form.publisher_location.data
            project.vol_issue_no = form.vol_issue_no.data
            project.doi_url = form.doi_url.data
            project.isbn_issn = form.isbn_issn.data
            project.web_of_science = form.web_of_science.data
            project.elsevier_scopus = form.elsevier_scopus.data
            project.elsevier_sciencedirect = form.elsevier_sciencedirect.data
            project.pubmed_medline = form.pubmed_medline.data
            project.ched_recognized = form.ched_recognized.data
            project.other_database = form.other_database.data
            project.citations = form.citations.data
            
            if form.clear_publication_proof.data:
                project.publication_proof = "none.png"
            elif form.publication_proof.data:
                project.publication_proof = form.publication_proof.data 
        
            if form.clear_utilization_proof.data:
                project.utilization_proof = "none.png"
            elif form.utilization_proof.data:
                project.utilization_proof = form.utilization_proof.data
            
            AuthorProject.query.filter_by(project_id=project.id).delete()
            EditorProject.query.filter_by(project_id=project.id).delete()
            db.session.commit()
            
            project.authors.clear()
            authors_data = form.authors.data.split(', ')
            for author_name in authors_data:
                author = Author.query.filter_by(name=author_name).first()
                if not author:
                    author = Author(name=author_name)
                    db.session.add(author)
                    db.session.commit()
                author_project = AuthorProject(author_id=author.id, project_id=project.id)
                db.session.add(author_project)
                
            project.editors.clear()
            editors_data = form.editors.data.split(', ')
            for editor_name in editors_data:
                editor = Editor.query.filter_by(name=editor_name).first()
                if not editor:
                    editor = Editor(name=editor_name)
                    db.session.add(editor)
                    db.session.commit()
                editor_project = EditorProject(editor_id=editor.id, project_id=project.id)
                db.session.add(editor_project)
            
            db.session.commit()
            flash('Project updated successfully', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template("projectform.html", mode=mode, form=form)