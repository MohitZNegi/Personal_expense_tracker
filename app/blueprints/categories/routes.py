from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Category, Expense
 
categories_bp = Blueprint("categories", __name__, template_folder="templates")
 
 
@categories_bp.route("/")
@login_required
def index():
    """List all categories for the logged-in user, with expense counts."""
    categories = (
        Category.query
        .filter_by(user_id=current_user.id)
        .order_by(Category.name)
        .all()
    )
    # Attach expense count to each category object for display
    for cat in categories:
        cat.expense_count = cat.expenses.count()
 
    return render_template("categories/index.html", categories=categories)
 
 
@categories_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Create a new category."""
    if request.method == "POST":
        name   = request.form.get("name", "").strip()
        colour = request.form.get("colour", "#6366f1").strip()
 
        if not name:
            flash("Category name is required.", "danger")
            return render_template("categories/add.html")
 
        # Check for duplicates scoped to this user
        existing = Category.query.filter_by(
            user_id=current_user.id,
            name=name
        ).first()
        if existing:
            flash(f'You already have a category called "{name}".', "warning")
            return render_template("categories/add.html")
 
        category = Category(
            name    = name,
            colour  = colour,
            user_id = current_user.id,
        )
        db.session.add(category)
        db.session.commit()
        flash(f'Category "{name}" created.', "success")
        return redirect(url_for("categories.index"))
 
    return render_template("categories/add.html")
 
 
@categories_bp.route("/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
def edit(category_id: int):
    """Edit an existing category — name or colour."""
    category = Category.query.get_or_404(category_id)
 
    # Security: only the owner may edit
    if category.user_id != current_user.id:
        abort(403)
 
    if request.method == "POST":
        new_name   = request.form.get("name", "").strip()
        new_colour = request.form.get("colour", category.colour).strip()
 
        if not new_name:
            flash("Category name cannot be empty.", "danger")
            return render_template("categories/edit.html", category=category)
 
        # Duplicate check — exclude the current category itself
        duplicate = Category.query.filter(
            Category.user_id == current_user.id,
            Category.name    == new_name,
            Category.id      != category_id,
        ).first()
        if duplicate:
            flash(f'Another category named "{new_name}" already exists.', "warning")
            return render_template("categories/edit.html", category=category)
 
        category.name   = new_name
        category.colour = new_colour
        db.session.commit()
        flash("Category updated.", "success")
        return redirect(url_for("categories.index"))
 
    return render_template("categories/edit.html", category=category)
 
 
@categories_bp.route("/<int:category_id>/delete", methods=["POST"])
@login_required
def delete(category_id: int):
    """
    Delete a category.
    Expenses that belonged to it become 'Uncategorised' (category_id set to NULL)
    rather than being deleted — SQLAlchemy handles this via the nullable FK.
    """
    category = Category.query.get_or_404(category_id)
 
    if category.user_id != current_user.id:
        abort(403)
 
    # Detach expenses from this category before deleting
    # (avoids a FK constraint error since category_id is nullable)
    Expense.query.filter_by(
        category_id = category_id,
        user_id     = current_user.id,
    ).update({"category_id": None})
 
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{category.name}" deleted. Its expenses are now uncategorised.', "info")
    return redirect(url_for("categories.index"))
 
 
@categories_bp.route("/<int:category_id>")
@login_required
def detail(category_id: int):
    """
    Show all expenses that belong to a specific category.
    Useful for drilling down from the summary page.
    """
    category = Category.query.get_or_404(category_id)
 
    if category.user_id != current_user.id:
        abort(403)
 
    expenses = (
        Expense.query
        .filter_by(category_id=category_id, user_id=current_user.id)
        .order_by(Expense.date.desc())
        .all()
    )
    total = sum(float(e.amount) for e in expenses)
 
    return render_template(
        "categories/detail.html",
        category = category,
        expenses = expenses,
        total    = total,
    )