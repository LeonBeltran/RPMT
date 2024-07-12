from rpmt import app, db
from rpmt.models import User

def init_db():
    with app.app_context():
        db.create_all()
        print(User.query.all())

if __name__ == '__main__':
    init_db()
