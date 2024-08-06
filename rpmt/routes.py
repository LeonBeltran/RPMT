from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from rpmt import app, db, bcrypt, upload_file, delete_file, get_file_url
from rpmt.forms import LoginForm, ProjectForm, SearchForm, UserForm
from rpmt.models import User, Project, Author, Editor, AuthorProject, EditorProject
import time
import os
import requests

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
        projects = projects.filter(Project.title.ilike(search_term))
        
    if form.author.data:
        author_search_term = f"%{form.author.data}%"
        projects = projects.join(AuthorProject).join(Author).filter(Author.name.ilike(author_search_term))

    if projects.all() == []:
        flash('This project does not exist. Please check if there are any mistakes.', 'danger')
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

@app.get('/download/<filename>')
def download_file(filename):
    name, _ = os.path.splitext(filename)
    if name == "none":
        flash('The file does not exist. Please upload the publication/utilization proof image or the pdf file of the research project/publication.', 'danger')
        return redirect(url_for('project_list'))
    else:
        try:
            # Use Supabase client to get a signed URL
            url = get_file_url(filename)

            # Fetch the file from the signed URL
            file_response = requests.get(url)
            
            if file_response.status_code == 200:
                return redirect(url, code=302)
            else:
                flash('Failed to download file. Please try again.', 'danger')
                return redirect(url_for('project_list'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}. Please contact the admin or developers if this persists.', 'danger')
            return redirect(url_for('project_list'))

# Admin: Register Page
# ----------------------------------------------------------------------------------------------
@app.get("/register")
def register():
    if current_user.is_authenticated:
        flash(f'Already logged in as {current_user.username}.', 'warning')
        return redirect(url_for('home'))
    form = UserForm()
    return render_template("register.html", form=form)

@app.post("/register")
def register_post():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        role = form.role.data

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template("register.html", form=form)
        
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(username=username, email=email, password=hashed_password, role=role)

        db.session.add(user)
        db.session.commit()
        
        flash('User Registeration Successful!', 'success')
        return redirect(url_for('login'))  # Redirect to the login page or any other page
    else:
        flash('Registration unsuccessful, please check your credentials.', 'danger')
    return render_template("register.html", form=form)

# Admin: Login Page
# ----------------------------------------------------------------------------------------------
@app.get("/login")
def login():
    if current_user.is_authenticated:
        flash(f'Already logged in as {current_user.username}.', 'warning')
        return redirect(url_for('home'))
    form = LoginForm()
    return render_template("login.html", form=form)

@app.post("/login")
def login_post():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # Login logic (checking username-password pair)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Logged in as {user.username}.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful, please check your credentials.', 'danger')
    return render_template("login.html", form=form)

# Logout
# ----------------------------------------------------------------------------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash(f'Logged out successfully.', 'success')
    return redirect(url_for('home'))

# Admin: Admin Area
# ----------------------------------------------------------------------------------------------
@app.get("/admin/")
@login_required
def admin():
    # Check author and editor list to ensure no empty authors/editors
    for author in Author.query.all():
        if author.projects == []:
            db.session.delete(author)
    for editor in Editor.query.all():
        if editor.projects == []:
            db.session.delete(editor)
    db.session.commit()
    return render_template("admin.html")

# Admin: Generate Projects Report
# ----------------------------------------------------------------------------------------------
@app.get("/admin/report")
@login_required
def report():
    form = SearchForm()
    authors = []
    author_data = []
    for author in authors:
        author_data.append(f"{author.name} has {len(author.projects)} project/s or publication/s")
    return render_template("report.html", form=form, author_data=author_data)

@app.post("/admin/report")
@login_required
def search_report():
    form = SearchForm()
    author_search_term = f"%{form.author.data}%"
    authors = Author.query.filter(Author.name.ilike(author_search_term)).all()
    author_data = []
    for author in authors:
        report = f"{author.name} has {len(author.projects)} project/s or publications/s."
        author_data.append(report)

    if author_data == []:
        flash('This author has not been added to the database. Please check if there are any mistakes.', 'danger')
    return render_template("report.html", form=form, author_data=author_data)

# Admin: Manage Account
# ----------------------------------------------------------------------------------------------
@app.get("/account/")
@login_required
def manage_account():
    user = User.query.filter_by(username=current_user.username).first()
    form = UserForm(
        username=user.username,
        email=user.email,
        role=user.role
    )
    return render_template("userpage.html", user=user, form=form)

@app.post("/account/")
def edit_credentials():
    user = User.query.filter_by(username=current_user.username).first()
    form = UserForm()
    if form.validate_on_submit():
        try:
            if bcrypt.check_password_hash(user.password, form.password.data):
                user.username = form.username.data
                user.email = form.email.data
                if form.new_password.data:
                    user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
                user.role = form.role.data
                db.session.commit()
                flash('User credentials updated successfully!', 'success')
            else:
                flash('Please input and confirm your old password.', 'warning')
            return redirect(url_for('manage_account'))
                
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}. Please contact the admin or developers if this persists.', 'danger')
            

@app.get("/account/delete")
@login_required
def delete_user():
    user = User.query.filter_by(username=current_user.username).first()
    if user.projects == []:
        logout_user()
        db.session.delete(user)
        db.session.commit()
        flash('User has been deleted.', 'danger')
        return redirect(url_for('home'))
    else: 
        # Prevent blank creator in projects
        flash('Please remove all projects before deleting this user.', 'warning')
        return redirect(url_for('admin'))

# Admin: Adding Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/add")
@login_required
def add_project():
    mode = "Adding a New Project"
    form = ProjectForm()
    return render_template("projectform.html", form=form, mode=mode)

# Function to append timestamp to filename to make unique filenames
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
            # Check for file uploads
            if form.publication_proof.data:
                publication_proof_filename = get_filename(form.publication_proof.data.filename)
                upload_file(publication_proof_filename, form.publication_proof.data)
            else:
                publication_proof_filename = "none.png"
            
            if form.utilization_proof.data:
                utilization_proof_filename = get_filename(form.utilization_proof.data.filename)
                upload_file(utilization_proof_filename, form.utilization_proof.data)
            else:
                utilization_proof_filename = "none.png"
            
            if form.pdf.data:
                pdf_filename = get_filename(form.pdf.data.filename)
                upload_file(pdf_filename, form.pdf.data)
            else:
                pdf_filename = "none.pdf"
                
            # Make new project instance
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
            
            # Add author and editor relationships
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
        
            flash('Project created successfully.', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}. Please contact the admin or developers if this persists.', 'danger')
    else:
        flash('Project creation failed, please try again.', 'danger')
    return render_template("projectform.html", form=form, mode=mode)

# Admin: Deleting Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/delete/")
@login_required
def delete_project_list():
    form = SearchForm()
    # Dept. Chair and Admin users may delete any added project
    if current_user.role == 'Chair' or current_user.role == 'Admin':
        projects = Project.query.all()
    # Faculty can delete projects they added
    else:
        projects = Project.query.filter_by(creator_id=current_user.id)
    return render_template("deleteprojectlist.html", data=projects, mode="Delete", form=form)

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
        projects = projects.filter(Project.title.ilike(search_term))
        
    if form.author.data:
        author_search_term = f"%{form.author.data}%"
        projects = projects.join(AuthorProject).join(Author).filter(Author.name.ilike(author_search_term))
        
    if projects.all() == []:
        flash('This project does not exist. Please check if there are any mistakes.', 'danger')
        projects = possible_projects
    return render_template("deleteprojectlist.html", data=projects, mode="Delete", form=form)

@app.get("/admin/delete/<int:paper_id>")
@login_required
def delete_project(paper_id):
    to_delete = Project.query.filter_by(id=paper_id).first()
    # Checking for valid user asking to delete
    if current_user.role == 'Chair' or current_user.role == 'Admin' or current_user.id == to_delete.creator_id:
        pub_filename = to_delete.publication_proof
        util_filename = to_delete.utilization_proof
        pdf_filename = to_delete.pdf
        
        # Delete existing files for project
        if pub_filename != 'none.png':
            delete_file(pub_filename)
        if util_filename != 'none.png':
            delete_file(util_filename)
        if pdf_filename != 'none.pdf':
            delete_file(pdf_filename)
        
        db.session.delete(to_delete)
        db.session.commit()
        flash('Successfully deleted project.', 'success')
    else:
        flash('You do not have permission to delete this project. Contact the project creator, admins or chair to delete this project.', 'danger')
    return redirect(url_for('admin'))

# Admin: Editing Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/edit/")
@login_required
def edit_project_list():
    form = SearchForm()
    # Dept. Chair and Admin users can edit all added projects
    if current_user.role == 'Chair' or current_user.role == 'Admin':
        projects = Project.query.all()
    # Faculty can access their added projects
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
        projects = projects.filter(Project.title.ilike(search_term))
    
    if form.author.data:
        author_search_term = f"%{form.author.data}%"
        projects = projects.join(AuthorProject).join(Author).filter(Author.name.ilike(author_search_term))
        
    if projects.all() == []:
        flash('This project does not exist. Please check if there are any mistakes.', 'danger')
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
        flash('You do not have permission to edit this project. Contact the project creator, admins or chair to edit this project.', 'danger')
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

            # Handle publication proof
            if form.clear_publication_proof.data:
                pub_filename = project.publication_proof
                if pub_filename != 'none.png':
                    delete_file(pub_filename)  # Delete from Supabase
                    project.publication_proof = "none.png"
            elif form.publication_proof.data:
                pub_filename = project.publication_proof
                if pub_filename != 'none.png':
                    delete_file(pub_filename)  # Delete from Supabase
                publication_proof_filename = get_filename(form.publication_proof.data.filename)
                upload_file(publication_proof_filename, form.publication_proof.data)
                project.publication_proof = publication_proof_filename

            # Handle utilization proof
            if form.clear_utilization_proof.data:
                util_filename = project.utilization_proof
                if util_filename != 'none.png':
                    delete_file(util_filename)  # Delete from Supabase
                    project.utilization_proof = "none.png"
            elif form.utilization_proof.data:
                util_filename = project.utilization_proof
                if util_filename != 'none.png':
                    delete_file(util_filename)  # Delete from Supabase
                utilization_proof_filename = get_filename(form.utilization_proof.data.filename)
                upload_file(utilization_proof_filename, form.utilization_proof.data)
                project.utilization_proof = utilization_proof_filename

            # Handle PDF
            if form.clear_pdf.data:
                pdf_filename = project.pdf
                if pdf_filename != 'none.pdf':
                    delete_file(pdf_filename)  # Delete from Supabase
                    project.pdf = "none.pdf"
            elif form.pdf.data:
                pdf_filename = project.pdf
                if pdf_filename != 'none.pdf':
                    delete_file(pdf_filename)  # Delete from Supabase
                pdf_filename = get_filename(form.pdf.data.filename)
                upload_file(pdf_filename, form.pdf.data)
                project.pdf = pdf_filename

            # Clear existing author and editor relationships
            AuthorProject.query.filter_by(project_id=project.id).delete()
            EditorProject.query.filter_by(project_id=project.id).delete()
            db.session.commit()

            # Add new authors
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

            # Add new editors
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
            flash('Project updated successfully.', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}. Please contact the admin or developers if this persists.', 'danger')

    return render_template("projectform.html", mode=mode, form=form)