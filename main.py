from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired
import requests
from sqlalchemy import desc

from db_functions import DbFunctions

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Any secret key add here'
Bootstrap5(app)
API_KEY = "Add your own api key here after signup to themoviedb.org"


# CREATE DB


class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies-collection.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE


class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(350), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(250), nullable=True)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    # db.drop_all()
    db.create_all()


class RatingForm(FlaskForm):
    rating = FloatField(label="Your Rating Out of 10 e.g. 4.5", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    done = SubmitField(label="Done", name="done")
    home = SubmitField(label="Home", name="home")


class AddMovieForm(FlaskForm):
    movie_title = StringField(label="Movie Title", validators=[DataRequired()])
    add_movie = SubmitField(label="Add Movie")


@app.route("/")
def home():
    # result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    # all_movies = result.scalars().all()
    all_movies = db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars().all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()

    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    my_rating_form = RatingForm()

    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    # result = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()

    if my_rating_form.home.data:
        return redirect(url_for("home"))

    if my_rating_form.validate_on_submit():
        rating = float(my_rating_form.rating.data)
        review = my_rating_form.review.data
        movie.rating = rating
        movie.review = review
        db.session.commit()

        return redirect(url_for("home"))
    return render_template("edit.html", form=my_rating_form, movie=movie)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        global DATA
        movie_title = form.movie_title.data
        url = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"
        params = {
            "api_key": API_KEY,
            "query": movie_title
        }
        response = requests.get(url=url, params=params)
        DATA = response.json()["results"]
        return render_template("select.html", options=DATA)
    return render_template("add.html", form=form)


@app.route("/find-movie")
def find_movie():
    movies_api_id = request.args.get("movie_id")

    if movies_api_id:
        url = f"https://api.themoviedb.org/3/movie/{movies_api_id}"
        params = {
            "api_key": API_KEY,
            "language": "en-US",
        }
        response = requests.get(url=url, params=params)
        data = response.json()
        print(movies_api_id)
        print(data)

        db_img_url = "https://image.tmdb.org/t/p/w500/"
        new_movie = Movie(
            title=data["title"],
            # The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"{db_img_url}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
