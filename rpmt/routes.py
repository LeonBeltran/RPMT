from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from rpmt import app, db, bcrypt
from rpmt.forms import LoginForm, ProjectForm, SearchForm
from rpmt.models import User, Project, Author, Editor, AuthorProject, EditorProject
import time
import os

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
    form = SearchForm()
    projects = Project.query.all()
    return render_template("projectlist.html", data=projects, mode="View", form=form)

@app.post("/projects/")
def search_projects():
    form = SearchForm()
    projects = Project.query
    
    if form.title.data:
        search_term = f"%{form.title.data}%"
        projects = projects.filter(Project.title.like(search_term))
        
    if form.author.data:
        author_search_term = f"%{form.author.data}%"
        projects = projects.join(AuthorProject).join(Author).filter(Author.name.like(author_search_term))

    if projects.all() == []:
        flash('Project not found', 'danger')
        projects = Project.query.all()
    return render_template("projectlist.html", data=projects, mode="View", form=form)

@app.get("/projects/<int:paper_id>")
def project_page(paper_id):
    project = Project.query.filter_by(id=paper_id).first()
    creator = User.query.filter_by(id=project.creator_id).first()
    creator_name = creator.username
    authors_data = ', '.join([ap.author.name for ap in project.authors])
    editors_data = ', '.join([ep.editor.name for ep in project.editors])
    return render_template("projectpage.html", project=project, creator=creator_name, authors=authors_data, editors=editors_data)

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
    authors = Author.query.all()
    author_data = []
    for author in authors:
        author_data.append(f"{author.name} has {len(author.projects)} project/s or publication/s")
    return render_template("report.html", author_data=author_data)

# Admin: Adding Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/add")
@login_required
def add_project():
    mode = "Adding a New Project"
    form = ProjectForm()
    return render_template("projectform.html", form=form, mode=mode)

def get_filename(filename):
    timestamp = int(time.time())
    name, extension = os.path.splitext(filename)
    return f"{name}_{timestamp}{extension}"

@app.post("/admin/add")
@login_required
def add_project_post():
    mode = "Adding a New Project"
    form = ProjectForm()
    if form.validate_on_submit():
        try:
            if form.publication_proof.data:
                publication_proof_filename = get_filename(form.publication_proof.data.filename)
                publication_proof_path = os.path.join(app.config['UPLOAD_FOLDER'], publication_proof_filename)
                form.publication_proof.data.save(publication_proof_path)
            else:
                publication_proof_filename = "none.png"
            
            if form.utilization_proof.data:
                utilization_proof_filename = get_filename(form.utilization_proof.data.filename)
                utilization_proof_path = os.path.join(app.config['UPLOAD_FOLDER'], utilization_proof_filename)
                form.utilization_proof.data.save(utilization_proof_path)
            else:
                utilization_proof_filename = "none.png"
            
            if form.pdf.data:
                pdf_filename = get_filename(form.pdf.data.filename)
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
                form.pdf.data.save(pdf_path)
            else:
                pdf_filename = "none.pdf"
                
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
                publication_proof=publication_proof_filename,
                utilization_proof=utilization_proof_filename,
                pdf=pdf_filename
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
    form = SearchForm()
    if current_user.role == 'Chair' or current_user.role == 'Admin':
        projects = Project.query.all()
    else:
        projects = Project.query.filter_by(creator_id=current_user.id)
    return render_template("projectlist.html", data=projects, mode="Delete", form=form)

@app.post("/admin/delete/")
@login_required
def search_delete_projects():
    form = SearchForm()
    
    if current_user.role == 'Chair' or current_user.role == 'Admin':
        possible_projects = Project.query
    else:
        possible_projects = Project.query.filter_by(creator_id=current_user.id)
    projects = possible_projects
        
    if form.title.data:
        search_term = f"%{form.title.data}%"
        projects = projects.filter(Project.title.like(search_term))
        
    if form.author.data:
        author_search_term = f"%{form.author.data}%"
        projects = projects.join(AuthorProject).join(Author).filter(Author.name.like(author_search_term))
        
    if projects.all() == []:
        flash('Project not found', 'danger')
        projects = possible_projects
    return render_template("projectlist.html", data=projects, mode="Delete", form=form)

def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

@app.get("/admin/delete/<int:paper_id>")
@login_required
def delete_project(paper_id):
    to_delete = Project.query.filter_by(id=paper_id).first()
    if current_user.role == 'Chair' or current_user.role == 'Admin' or current_user.id == to_delete.creator_id:
        pub_filename = to_delete.publication_proof
        util_filename = to_delete.utilization_proof
        pdf_filename = to_delete.pdf
        
        if pub_filename != 'none.png':
            delete_file(pub_filename)
        if util_filename != 'none.png':
            delete_file(util_filename)
        if pdf_filename != 'none.pdf':
            delete_file(pdf_filename)
        
        db.session.delete(to_delete)
        db.session.commit()
        flash('Successfully deleted project', 'success')
    else:
        flash('You do not have permission to delete this project', 'danger')
    return redirect(url_for('admin'))

# Admin: Editing Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/edit/")
@login_required
def edit_project_list():
    form = SearchForm()
    if current_user.role == 'Chair' or current_user.role == 'Admin':
        projects = Project.query.all()
    else:
        projects = Project.query.filter_by(creator_id=current_user.id)
    return render_template("projectlist.html", data=projects, mode="Edit", form=form)

@app.post("/admin/edit/")
@login_required
def search_edit_projects():
    form = SearchForm()
    if current_user.role == 'Chair' or current_user.role == 'Admin':
        possible_projects = Project.query
    else:
        possible_projects = Project.query.filter_by(creator_id=current_user.id)
    projects = possible_projects
        
    if form.title.data:
        search_term = f"%{form.title.data}%"
        projects = projects.filter(Project.title.like(search_term))
        
    if projects.all() == []:
        flash('Project not found', 'danger')
        projects = possible_projects
    return render_template("projectlist.html", data=projects, mode="Edit", form=form)

@app.get("/admin/edit/<int:paper_id>")
@login_required
def edit_project(paper_id):
    project = Project.query.filter_by(id=paper_id).first()
    if current_user.role == 'Chair' or current_user.role == 'Admin' or current_user.id == project.creator_id:
        mode = "Editing " + project.title
        
        authors_data = ', '.join([ap.author.name for ap in project.authors])
        editors_data = ', '.join([ep.editor.name for ep in project.editors])
        
        form = ProjectForm(obj=project)
        form.authors.data = authors_data
        form.editors.data = editors_data

        return render_template("projectform.html", mode=mode, form=form)
    else:
        flash('You do not have permission to edit this project', 'danger')
        return redirect(url_for('admin'))
    
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
                pub_filename = project.publication_proof
                if pub_filename != 'none.png':
                    delete_file(pub_filename)
                    project.publication_proof = "none.png"
            elif form.publication_proof.data:
                pub_filename = project.publication_proof
                if pub_filename != 'none.png':
                    delete_file(pub_filename)
                publication_proof_filename = get_filename(form.publication_proof.data.filename)
                publication_proof_path = os.path.join(app.config['UPLOAD_FOLDER'], publication_proof_filename)
                form.publication_proof.data.save(publication_proof_path)
                project.publication_proof = publication_proof_filename
        
            if form.clear_utilization_proof.data:
                util_filename = project.utilization_proof
                if util_filename != 'none.png':
                    delete_file(util_filename)
                    project.utilization_proof = "none.png"
            elif form.utilization_proof.data:
                util_filename = project.utilization_proof
                if util_filename != 'none.png':
                    delete_file(util_filename)
                utilization_proof_filename = get_filename(form.utilization_proof.data.filename)
                utilization_proof_path = os.path.join(app.config['UPLOAD_FOLDER'], utilization_proof_filename)
                form.utilization_proof.data.save(utilization_proof_path)
                project.utilization_proof = utilization_proof_filename
                
            if form.clear_pdf.data:
                pdf_filename = project.pdf
                if pdf_filename != 'none.pdf':
                    delete_file(pdf_filename)
                    project.pdf = "none.pdf"
            elif form.pdf.data:
                pdf_filename = project.pdf
                if pdf_filename != 'none.pdf':
                    delete_file(pdf_filename)
                pdf_filename = get_filename(form.pdf.data.filename)
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
                form.pdf.data.save(pdf_path)
                project.pdf = pdf_filename
            
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