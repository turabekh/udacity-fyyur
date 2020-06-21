from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.fields.html5 import DateTimeLocalField, TelField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError
from helper import GENRES, STATES
from app import Artist, Venue
import phonenumbers

class ShowForm(Form):
    artist_id = SelectField(
        'artist_id', validators=[DataRequired()],
        choices= [(art.id, art.name) for art in Artist.query.all()]
    )
    venue_id =SelectField(
        'venue_id', validators=[DataRequired()],
        choices= [(ven.id, ven.name) for ven in Venue.query.all()]
    )
    start_time = DateTimeLocalField('start_time', validators=[DataRequired()], default= datetime.today())

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices= STATES
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = TelField()
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices = GENRES
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    seeking_talent = BooleanField("Seeking Talent")
    seeking_description = StringField(
        'Seeking Description'
    )
    website = StringField("Website")

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices = STATES
    )
    phone = TelField()
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices = GENRES
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    seeking_venue = BooleanField("Seeking Talent")
    seeking_description = StringField(
        'Seeking Description'
    )
    website = StringField("Website")

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')