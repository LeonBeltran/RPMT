from flask import Flask, render_template, redirect

app = Flask(__name__)

# Home Page
# ----------------------------------------------------------------------------------------------
@app.get("/")
@app.get("/home")
def home():
    return render_template("home.html")

# Projects Page
# ----------------------------------------------------------------------------------------------
dummy_data = [
    {
        "ID": 0,
        "Name": "Bro L. Loan"    
    },
    {
        "ID": 1,
        "Name": "Kar R. Igan"    
    },
    {
        "ID": 2,
        "Name": "Jame W. Time"    
    },
    {
        "ID": 3,
        "Name": "Robin S. Kool"    
    },
    {
        "ID": 4,
        "Name": "Pasha B. Friend"    
    },
    {
        "ID": 5,
        "Name": "Sasha S. Bench (Bottom textBottom textBottom textBottom textBottom textBottom textBottom textBottom textBottom textBottom text)"    
    },
    {
        "ID": 6,
        "Name": "Aut quasi perspiciatis qui adipisci eveniet et repudiandae omnis ut eligendi nostrum aut doloribus ducimus a provident consequatur ut distinctio commodi."    
    }
]

@app.get("/projects/")
def list_projects():
    return render_template("projectlist.html", data=dummy_data, mode="View")
@app.get("/projects/<int:paper_id>")
def show_project(paper_id):
    return render_template("projectpage.html", project=dummy_data[paper_id])

# Admin: Login Page
# ----------------------------------------------------------------------------------------------
@app.get("/login")
def login_get():
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
def show_projects_report():
    return render_template("report.html")

# Admin: Adding Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/add")
def add_project_get():
    return render_template("projectform.html")

@app.post("/admin/add")
def add_project_post():
    return render_template("projectform.html")

# @app.get("/admin/add/info")
# @app.post("/admin/add/info")

# @app.get("/admin/add/authors")
# def add_project_authors_get():
#     return "<p>GET Add Project Authors </p>"

# @app.post("/admin/add/authors")
# def add_project_authors_post():
#     return "<p>POST Add Project Authors</p>"

# @app.get("/admin/add/editors")
# def add_project_editors_get():
#     return "<p>GET Add Project Editors </p>"

# @app.post("/admin/add/editors")
# def add_project_editors_post():
#     return "<p>POST Add Project Editors</p>"

# Admin: Deleting Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/delete/")
def admin_delete_projects():
    return render_template("projectlist.html", data=dummy_data, mode="Delete")

@app.get("/admin/delete/<int:paper_id>")
def delete_project(paper_id):
    data = [dummy_data[paper_id]]
    return render_template("projectlist.html", data=data, mode="Deleted")

# Admin: Editing Projects
# ----------------------------------------------------------------------------------------------
@app.get("/admin/edit/")
def admin_edit_projects():
    return render_template("projectlist.html", data=dummy_data, mode="Edit")

@app.get("/admin/edit/<int:paper_id>")
def edit_project_get(paper_id):
    mode = "Editing " + dummy_data[paper_id]["Name"]
    return render_template("projectform.html", mode=mode)
@app.post("/admin/edit/<int:paper_id>")
def edit_project_post(paper_id):
    mode = "Edited " + dummy_data[paper_id]["Name"]
    return render_template("projectform.html", mode=mode)

if __name__ == '__main__':
    app.run(debug=True)