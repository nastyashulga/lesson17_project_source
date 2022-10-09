# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False}
db = SQLAlchemy(app)

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    genre = fields.Nested(GenreSchema)
    director_id = fields.Int()
    director = fields.Nested(DirectorSchema)



movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

api = Api(app)
movie_ns = api.namespace('movies')

db.create_all()

@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        all_movies = Movie.query

        page = request.args.get('page')
        director_id = request.args.get('director_id')
        if director_id:
            all_movies = all_movies.filter(Movie.director_id == director_id)

        genre_id = request.args.get('genre_id')
        if director_id:
            all_movies = all_movies.filter(Movie.genre_id == genre_id)

        result = movies_schema.dump(all_movies), 200

        if page:
            page = int(page)
            result = result[page * 2:(page + 1) * 2]

        return result

    def post(self):
        req_json = request.json
        try:
            new_movie = Movie(**req_json)
            with db.session.begin():
                db.session.add(new_movie)
                db.session.commit()
            return "", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 200

@movie_ns.route('/<int:uid>')
class MoviesView(Resource):
    def get(self, uid):
        one_movie = Movie.query.get(uid)
        return movie_schema.dump(one_movie), 200

    def put(self, uid):
        req_json = request.json

        try:
            db.session.query(Movie).filter(Movie.id == uid).update(
                req_json
            )
            db.session.commit()
            return "", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 200

    def delete(self, uid):
        try:
            db.session.query(Movie).filter(Movie.id == uid).delete()
            db.session.commit()
            return "", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 200


if __name__ == '__main__':
    app.run(debug=True, port=4567)
