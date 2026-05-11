from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """
    UserMixin gives us: is_authenticated, is_active, get_id() — 
    everything Flask-Login needs. We just add our own fields on top.
    """
    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One user has many expenses (one-to-many relationship)
    expenses   = db.relationship("Expense", backref="owner", lazy="dynamic",
                                  cascade="all, delete-orphan")
    categories = db.relationship("Category", backref="owner", lazy="dynamic",
                                  cascade="all, delete-orphan")

    # --- Class methods (OOP best practice: behaviour lives with data) ---

    def set_password(self, password: str) -> None:
        """Never store plain-text passwords. Always hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_email(cls, email: str) -> "User | None":
        """Query helper — keeps SQL out of route handlers."""
        return cls.query.filter_by(email=email.lower()).first()

    def __repr__(self) -> str:
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id: int) -> User | None:
    return User.query.get(int(user_id))