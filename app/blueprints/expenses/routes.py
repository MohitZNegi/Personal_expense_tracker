from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Expense, Category
from datetime import date

expenses_bp = Blueprint("expenses", __name__, template_folder="templates")

@expenses_bp.route("/")
@login_required
def index():
    expenses = Expense.query.filter_by(user_id=current_user.id)\
                            .order_by(Expense.date.desc()).all()
    return render_template("expenses/index.html", expenses=expenses)


@expenses_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    categories = Category.get_user_categories(current_user.id)

    if request.method == "POST":
        description = request.form.get("description", "").strip()
        amount      = request.form.get("amount")
        expense_date = request.form.get("date") or str(date.today())
        category_id = request.form.get("category_id") or None
        notes       = request.form.get("notes", "").strip()

        if not description or not amount:
            flash("Description and amount are required.", "danger")
            return render_template("expenses/add.html", categories=categories)

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Amount must be a positive number.", "danger")
            return render_template("expenses/add.html", categories=categories)

        expense = Expense(
            description = description,
            amount      = amount,
            date        = date.fromisoformat(expense_date),
            category_id = int(category_id) if category_id else None,
            notes       = notes,
            user_id     = current_user.id,
        )
        db.session.add(expense)
        db.session.commit()
        flash("Expense added.", "success")
        return redirect(url_for("expenses.index"))

    return render_template("expenses/add.html", categories=categories)


@expenses_bp.route("/<int:expense_id>/edit", methods=["GET", "POST"])
@login_required
def edit(expense_id: int):
    # abort(403) if this expense belongs to someone else — security check
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        abort(403)

    categories = Category.get_user_categories(current_user.id)

    if request.method == "POST":
        expense.description = request.form.get("description", "").strip()
        expense.amount      = float(request.form.get("amount", 0))
        expense.date        = date.fromisoformat(request.form.get("date"))
        expense.category_id = request.form.get("category_id") or None
        expense.notes       = request.form.get("notes", "").strip()
        db.session.commit()
        flash("Expense updated.", "success")
        return redirect(url_for("expenses.index"))

    return render_template("expenses/edit.html", expense=expense, categories=categories)


@expenses_bp.route("/<int:expense_id>/delete", methods=["POST"])
@login_required
def delete(expense_id: int):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        abort(403)
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.", "success")
    return redirect(url_for("expenses.index"))


@expenses_bp.route("/summary")
@login_required
def summary():
    from datetime import datetime
    year  = request.args.get("year",  datetime.now().year,  type=int)
    month = request.args.get("month", datetime.now().month, type=int)

    monthly_total = Expense.get_monthly_total(current_user.id, year, month)
    by_category   = Expense.get_by_category(current_user.id)

    return render_template("expenses/summary.html",
                           monthly_total=monthly_total,
                           by_category=by_category,
                           year=year, month=month)