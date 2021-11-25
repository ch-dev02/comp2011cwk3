from flask import render_template, flash, request, redirect, Blueprint, url_for
from app import app, db, models
from .forms import CreateTaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import logging

auth = Blueprint('auth', __name__)

@auth.route('/')
def login():
    if current_user.is_authenticated:
        app.logger.warning('Attempted Login Page when already logged in')
        return redirect("/groups")
    return render_template('login.html')

@auth.route('/', methods=['POST'])
def login_post():
    if current_user.is_authenticated:
        app.logger.warning('Attempted Login Page (with POST) when already logged in')
        return redirect("/groups")
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = models.User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.', 'error')
        app.logger.error('Attempted Login with incorrect details')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    login_user(user, remember=remember)
    return redirect("/groups")

@auth.route('/signup')
def signup():
    if current_user.is_authenticated:
        app.logger.warning('Attempted Sign Up Page when already logged in')
        return redirect("/groups")
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    if current_user.is_authenticated:
        app.logger.warning('Attempted Sign Up Page (with POST) when already logged in')
        return redirect("/groups")
    username = request.form.get('username')
    password = request.form.get('password')

    user = models.User.query.filter_by(username=username).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Username already exists', 'error')
        app.logger.error('Attempted Sign Up when username taken')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = models.User(username=username, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html', page_title="Profile: "+current_user.username, title='Group To-Do | Profile')

@auth.route('/change_pwd', methods=['POST'])
@login_required
def change_pwd():
    old = request.form.get('old_password')
    new = request.form.get('new_password')
    user = models.User.query.filter_by(username=current_user.username).first()

    if not user or not check_password_hash(user.password, old):
        flash('Incorrect password', 'error')
        app.logger.error('Attempted to change password with incorrect password')
        return redirect(url_for('auth.profile'))
    
    user.password=generate_password_hash(new, method='sha256')
    db.session.commit()

    flash('Password changed successfully')
    app.logger.info('Password changed for user:' + current_user.username)
    return redirect(url_for('auth.profile'))