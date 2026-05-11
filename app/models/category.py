from app.extensions import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = "categories"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(50), nullable=False)
    colour     = db.Column(db.String(7), default="#6366f1")  # hex colour for UI
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key — every category belongs to one user
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # One category has many expenses
    expenses   = db.relationship("Expense", backref="category", lazy="dynamic")

    @classmethod
    def get_user_categories(cls, user_id: int) -> list["Category"]:
        return cls.query.filter_by(user_id=user_id).order_by(cls.name).all()

    def __repr__(self) -> str:
        return f"<Category {self.name}>"