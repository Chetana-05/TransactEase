from app import create_app
from extensions import db
import os

def init_db():
    # Delete existing database file
    if os.path.exists('transactions.db'):
        os.remove('transactions.db')
        print("Removed existing database.")

    # Create new database with updated schema
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Created new database with updated schema.")

if __name__ == '__main__':
    init_db() 