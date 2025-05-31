from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    login = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    # created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<User {self.login}>'
