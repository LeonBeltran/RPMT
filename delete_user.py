from rpmt import app, db
from rpmt.models import User
import sys

def delete_user(username):
    with app.app_context():
        # Find user
        user = User.query.filter_by(username=username).first()
        if user:
            # Delete user
            db.session.delete(user)
            db.session.commit()
            print(f"User {username} deleted successfully!")
        else:
            print(f"No user found with username: {username}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python delete_user.py <username>")
    else:
        username = sys.argv[1]
        delete_user(username)
