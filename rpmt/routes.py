from flask import render_template, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user
from rpmt import app, db, bcrypt
from rpmt.forms import LoginForm
from rpmt.models import User

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
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful, please check your username and password. Contact the site administrators if you believe something is wrong.', 'danger')
    
    return render_template("login.html", form=form)

# Logout
# ----------------------------------------------------------------------------------------------
@app.route("/logout")
def logout():
    logout_user()
    flash(f'Logged out successfully', 'success')
    return redirect(url_for('home'))

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