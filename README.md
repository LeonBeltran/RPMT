# Research Project Management Tool
CS 195 Internship Project for MY 2024 under Department of Industrial Engineering and Operations Research

## Start Server
* Instructions are in MACOS format

### RPMT.exe
1. Download zip file in latest release
2. Unzip the file
3. Run the exe file
4. Open ```http://127.0.0.1:5000``` in your browser or open the link shown in the terminal

### Localhost
1. Clone the repository.
```git clone [REPO_URL]```
2. Open terminal and go to root folder path.
```cd [PATH/TO/ROOT]```
3. Start up a Python virtual environment.
```python3 -m venv [VENV_FOLDER_NAME]```
```source [VENV_FOLDER_NAME]/bin/activate```
4. Download the project dependencies.
```pip install -r requirements.txt```
5. Run app.py to start the server in debug mode.
```python3 app.py```
6. Open http://127.0.0.1:5000 to view the web application.

## User Management
### Deleting Users
```python3 delete_user.py [USERNAME]```
- This is for localhost runs only