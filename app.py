from flask import Flask, render_template, url_for, redirect, request, flash
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, BooleanField
from wtforms.validators import InputRequired, Optional, NumberRange, URL
import requests as r
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ihaveanothersecret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/adopt-a-pet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db = SQLAlchemy(app)
toolbar = DebugToolbarExtension(app)

pf_api_key = '80345b20b4cf0018e7a3baefae81ed42'


class Pet(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    species = db.Column(db.Text, nullable=False)
    photo_url = db.Column(db.Text)
    age = db.Column(db.Integer)
    notes = db.Column(db.Text)
    available = db.Column(db.Boolean, default=True)


db.create_all()


class AddPetForm(FlaskForm):
    """ Form for adding pets. """

    name = StringField("Name of Friend", validators=[InputRequired()])
    species = StringField("Species of Friend", validators=[InputRequired()])
    photo_url = StringField("Image URL", validators=[URL(), Optional()])
    age = IntegerField(
        "Age of Friend", validators=[InputRequired(),
                                     NumberRange(max=30)])
    notes = StringField("Additional Notes")
    available = BooleanField("Available?", default='checked')


class EditPetForm(FlaskForm):
    """ Form for editing pets """

    photo_url = StringField("Image URL")
    notes = StringField("Additional Notes")
    available = BooleanField("Available?", default='checked')


# TODO: Fix edge case where get doesn't work
# Get a random pet from PetFinder
def get_random_pet():
    req = r.get("http://api.petfinder.com/pet.getRandom", {
        "key": pf_api_key,
        "format": "json",
        "output": "basic"
    })
    return req.json()['petfinder']['pet']


@app.route('/')
def pets_index():
    """ Shows all pets """

    pets = Pet.query.all()
    random_pet = get_random_pet()

    return render_template('index.html', pets=pets, random_pet=random_pet)


@app.route('/add', methods=['GET', 'POST'])
def show_add_form():
    """ Show form to add pets; handle adding pets """

    form = AddPetForm()

    if form.validate_on_submit():
        name = form.data['name']
        species = form.data['species']
        photo_url = form.data['photo_url']
        age = form.data['age']
        notes = form.data['notes']
        available = form.data['available']

        newPet = Pet(
            name=name,
            species=species,
            photo_url=photo_url,
            age=age,
            notes=notes,
            available=available)
        db.session.add(newPet)
        db.session.commit()
        return redirect(url_for('pets_index'))

    else:
        return render_template('pet_add_form.html', form=form)


@app.route('/see/<int:pet_id>')
def show_pet_details(pet_id):
    """ See details for pet for given pet_id """

    pet = Pet.query.get(pet_id)
    return render_template('show_pet.html', pet=pet)


@app.route('/edit/<int:pet_id>', methods=['GET', 'POST'])
def edit_pet_details(pet_id):
    """ Show the edit pet details form for given pet_id """

    pet = Pet.query.get(pet_id)
    form = EditPetForm(obj=pet)

    if form.validate_on_submit():
        pet.photo_url = form.data["photo_url"]
        pet.notes = form.data["notes"]
        pet.available = form.data["available"]
        db.session.commit()
        return redirect(url_for('pets_index'))
    else:
        return render_template('edit_pet.html', form=form, pet=pet)


from IPython import embed
embed()
