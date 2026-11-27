from flask import Flask, request, render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import argon2
import os

from marshmallow import Schema, fields

#Initialize app
db = SQLAlchemy()

app = Flask(__name__)

ph = argon2.PasswordHasher()

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db.init_app(app)
migrate = Migrate(app, db)

#Define Models
class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    grade_level = db.Column(db.Integer)
    edition = db.Column(db.String(50))
    status = db.Column(db.String(50), nullable=False)
    creation_datetime = db.Column(db.DateTime)
    pledged_school = db.Column(db.String(200))

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    owner = db.relationship("User", back_populates="owned_books")

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    grade_level = db.Column(db.Integer)

    school = db.Column(db.String(200))
    city = db.Column(db.String(150), nullable=False)

    owned_books = db.relationship("Book", back_populates="owner", cascade="all, delete-orphan")

    password_hash = db.Column(db.String(128))

#Marshmallow Schemas
class BookSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    grade_level = fields.Int()
    edition = fields.Str()
    status = fields.Str()
    creation_datetime = fields.DateTime()
    pledged_school = fields.Str()

    owner_id = fields.Int()

class UserSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    grade_level = fields.Int()
    school = fields.Str()
    city = fields.Str()

bookschema = BookSchema()
userschema = UserSchema()

#Define endpoints
@app.route("/adduser", methods=["POST"])
def create_new_user():
    name = str(request.args.get("name"))
    grade_level = int(request.args.get("grade_level"))
    school = str(request.args.get("school"))
    city = str(request.args.get("city"))
    password_hash = ph.hash(request.args.get("password"))

    if not name or not city or not password_hash:
        return {"error": "Not all required fields provided"}, 400

    prev_user_id = db.session.query(db.func.max(User.id)).scalar()
    
    if prev_user_id is None:
        user_id = 1
    else:
        user_id = prev_user_id + 1

    new_user = User(
        id = user_id,
        name = name,
        grade_level = grade_level,
        school = school,
        city = city,
        password_hash = password_hash
    )

    db.session.add(new_user)
    db.session.commit()

    return {"message": "User added successfully", "user_id": user_id}, 201

@app.route("/user/<int:user_id>/addbook", methods=["POST"])
def add_book_to_user(user_id):
    prev_book_id = db.session.query(db.func.max(Book.id)).scalar()
        
    if prev_book_id is None:
        book_id = 1
    else:
        book_id = prev_book_id + 1

    name = request.args.get("name")
    grade_level = request.args.get("grade_level")
    edition = request.args.get("edition")
    status = request.args.get("status")
    creation_datetime = datetime.now()

    if not name or not status:
        return {"error": "Not all required fields provided"}, 400

    new_book = Book(
        id = book_id,
        name = name,
        grade_level = grade_level,
        edition = edition,
        status = status,
        creation_datetime = creation_datetime,
        owner_id = user_id
    )

    db.session.add(new_book)
    db.session.commit()

    return {"message": "Book created successfully"}, 201

@app.route("/user/<int:user_id>/removebook/<int:book_id>", methods=["POST"])
def remove_book_from_user(user_id, book_id):
    user = db.session.get(User, user_id)
    book = db.session.get(Book, book_id)

    db.session.delete(book)

    db.session.commit()

    return {"Deletion Successful": "The book was successfully deleted from the user's account."}, 200

@app.route("/<string:city>/find_match/<string:book_name>", methods=["GET"])
@app.route("/<string:city>/find_match/<string:book_name>/edition/<int:book_edition>", methods=["GET"])
def main_book_search(book_name, city, book_edition=1):
    possible_receivers = User.query.filter_by(city=city).join(Book).filter(Book.name == book_name, Book.edition == str(book_edition), Book.status == "wanted").all()

    schools_need_list = {}
    for receiver in possible_receivers:
        try:
            school_stu_needed_count = schools_need_list[receiver.school]
        except KeyError:
            school_stu_needed_count = 0

        if school_stu_needed_count:
            school_stu_needed_count += 1
        else:
            school_stu_needed_count = 1

        schools_need_list[receiver.school] = school_stu_needed_count

    return jsonify(schools_need_list), 200

@app.route("/from/<int:giver_id>/to/<string:school_name>/pledge/<string:book_name>", methods=["GET"])
@app.route("/from/<int:giver_id>/to/<string:school_name>/pledge/<string:book_name>/edition/<int:book_edition>", methods=["GET"])
def pledge_book(giver_id, school_name, book_name, book_edition=1):
    earliest_receiver = User.query.filter_by(school=school_name).join(Book).filter(Book.name == book_name, Book.edition == str(book_edition), Book.status == "wanted").order_by(Book.creation_datetime).first()

    target_book = Book.query.filter_by(name=book_name, edition=str(book_edition), status="wanted").join(User).filter(User.id == earliest_receiver.id).first()
    target_book.status = "in fulfillment"

    giver_book = Book.query.filter_by(name=book_name, edition=str(book_edition)).join(User).filter(User.id == giver_id).first()
    giver_book.status = "fulfilling"
    giver_book.pledged_school = school_name

    db.session.commit()

    return {"Success": "The book has been successfully pledged."}, 200

@app.route("/deliver_book/<int:book_id>", methods=["POST"])
def deliver_book(book_id):
    giver_book = db.session.get(Book, book_id)

    receiver_book = Book.query.filter_by(name=giver_book.name, edition=str(giver_book.edition)).join(User).filter(User.school == giver_book.pledged_school).order_by(Book.creation_datetime).first()

    receiver_book.status = "delivered"
    giver_book.status = "donated"

    db.session.commit()

    return {"Success": "The book has been successfully marked as delivered."}, 200

@app.route("/confirm_delivery/<int:book_id>", methods=["POST"])
def confirm_book_delivery(book_id):
    book = db.session.get(Book, book_id)

    book.status = "owned"

    db.session.commit()

    return {"Success": "The book is officially in your possession."}, 200

@app.route("/user/<int:user_id>", methods=["GET"])
def get_user_info(user_id):
    user = db.session.get(User, user_id)

    return_data = {}
    return_data['name'] = user.name
    return_data['grade_level'] = user.grade_level
    return_data['school'] = user.school
    return_data['city'] = user.city

    return jsonify(return_data), 200

@app.route("/authuser", methods=["POST"])
def authuser():
    userid = int(request.args.get("userid"))
    password = str(request.args.get("password"))

    if not userid or not password:
        return {"error": "Not all required data provided"}, 400

    user = db.session.get(User, userid)
    pw_hash = user.password_hash

    try:
        ph.verify(pw_hash, password)
    except argon2.exceptions.VerifyMismatchError:
        return {"error": "Invalid credentials"}, 401

    return {"message": "User successfully authorized"}, 200

@app.route("/user/<int:user_id>/books", methods=["GET"])
def get_user_books(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return {"error": "User not found"}, 404

    books = bookschema.dump(user.owned_books, many=True)

    return jsonify(books), 200