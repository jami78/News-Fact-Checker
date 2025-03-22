from sqlalchemy.orm import Session
from app.models.users import User
from app.auth.auth import verify_password

def authenticate_user(db: Session, username: str, password: str):
    """ Authenticates a user by verifying password. """
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def get_user(db: Session, username: str):
    """ Retrieves a user from the database. """
    return db.query(User).filter(User.username == username).first()
