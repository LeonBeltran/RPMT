from rpmt import app, db
from rpmt.models import User

def list_users():
    with app.app_context():
        users = User.query.all()
        if users:
            for user in users:
                print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
        else:
            print("No users found.")

if __name__ == '__main__':
    list_users()
