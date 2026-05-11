from app.extensions import db
from datetime import datetime, date

class Expense(db.Model):
    __tablename__ = "expenses"

    id          = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount      = db.Column(db.Numeric(10, 2), nullable=False)  # precise decimal, not float
    date        = db.Column(db.Date, nullable=False, default=date.today)
    notes       = db.Column(db.Text, nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    # --- Query class methods ---

    @classmethod
    def get_monthly_total(cls, user_id: int, year: int, month: int) -> float:
        """Return total spending for a given month."""
        from sqlalchemy import func, extract
        result = db.session.query(func.sum(cls.amount)).filter(
            cls.user_id == user_id,
            extract("year",  cls.date) == year,
            extract("month", cls.date) == month,
        ).scalar()
        return float(result or 0)

    @classmethod
    def get_by_category(cls, user_id: int) -> list[dict]:
        """Return spending grouped by category — used for the summary page."""
        from sqlalchemy import func
        from app.models.category import Category
        return (
            db.session.query(Category.name, Category.colour, func.sum(cls.amount).label("total"))
            .join(cls, cls.category_id == Category.id)
            .filter(cls.user_id == user_id)
            .group_by(Category.id)
            .all()
        )

    def __repr__(self) -> str:
        return f"<Expense {self.description} £{self.amount}>"