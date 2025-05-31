from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import uuid


db = SQLAlchemy()

# Only storing revoked tokens. Yet unrevoked ones must be valid.
class RevokedToken(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    jti = db.Column(db.String(36), nullable=False, index=True)
    token_type = db.Column(db.String(10), nullable=False)
    user_login = db.Column(db.String(120), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RevokedToken {self.jti} for {self.user_login}>'

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jwt.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

def is_token_revoked(jti):
    return RevokedToken.query.filter_by(jti=jti).first() is not None

def revoke_token(jti, token_type, user_login, expires_at):
    if not is_token_revoked(jti):
        new_revoked = RevokedToken(
            jti=jti,
            token_type=token_type,
            user_login=user_login,
            expires_at=expires_at
        )
        db.session.add(new_revoked)
        db.session.commit()

def cleanup_revoked_tokens():
    expired = RevokedToken.query.filter(RevokedToken.expires_at < datetime.utcnow()).all()
    for token in expired:
        db.session.delete(token)
    db.session.commit()
