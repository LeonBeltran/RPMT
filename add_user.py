from rpmt import app, db, bcrypt
from rpmt.models import User
import sys

def add_user(username, email, password, role):
    with app.app_context():
        # Create new user
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        
        # Commit new user
        db.session.add(new_user)
        db.session.commit()
        print(f"User {new_user} added successfully!")

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python add_user.py <username> <email> <password> <role>")
    else:
        username, email, password, role = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
        add_user(username, email, password, role)
