from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'devsecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    from .routes import main
    app.register_blueprint(main)

    return app
#####  step 4:models.py#####
from . import db
from flask_login import UserMixin
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(200))
    review_text = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  ##### step 5:app.py#####

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=25)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class ReviewForm(FlaskForm):
    book_title = StringField('Book Title', validators=[InputRequired()])
    review_text = TextAreaField('Review', validators=[InputRequired()])
    submit = SubmitField('Submit Review')
#####Step 6  : recommender.py######
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

data = pd.read_csv('data/books.csv')
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(data['description'].fillna(''))
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

indices = pd.Series(data.index, index=data['title'].str.lower())

def recommend_books(title):
    idx = indices.get(title.lower())
    if idx is None:
        return []
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]
    book_indices = [i[0] for i in sim_scores]
    return data['title'].iloc[book_indices].tolist()

