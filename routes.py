from flask import Blueprint, render_template, redirect, url_for, request
from .forms import RegisterForm, LoginForm, ReviewForm
from .models import User, Review
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .recommender import recommend_books

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
    return render_template('login.html', form=form)

@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = ReviewForm()
    reviews = Review.query.filter_by(user_id=current_user.id).all()
    if form.validate_on_submit():
        review = Review(book_title=form.book_title.data,
                        review_text=form.review_text.data,
                        user_id=current_user.id)
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('dashboard.html', form=form, reviews=reviews)

@main.route('/recommend', methods=['GET'])
@login_required
def recommend():
    book = request.args.get('book')
    recs = recommend_books(book) if book else []
    return render_template('recommendation.html', recommendations=recs, searched=book)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
 
