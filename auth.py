from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from werkzeug.security import check_password_hash

# creates blueprint for authentication routes
auth_routes = Blueprint('auth_routes', __name__)

# login Route (redirects to dashboard if user is already logged in)
@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in!", "info")
        return redirect(url_for('product_routes.dashboard')) 
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # checks if user exists and password is correct
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('product_routes.dashboard'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')

# logout route
@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))
