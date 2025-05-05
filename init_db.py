from app import app, db
from flask_migrate import upgrade

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.") 