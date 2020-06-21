#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class City(db.Model):
  __tablename__ = "City"
  id = db.Column(db.Integer, primary_key=True) 
  name = db.Column(db.String(120))
  state = db.Column(db.String(10))
  venues = db.relationship("Venue", backref="city_parent", lazy=True)

  def show_venue(self):
    venues = [v.show_venues() for v in self.venues]
    if len(venues) < 1:
      return None
    d = {
      "city": self.name,
      "state": self.state,
      "venues": venues,
    }
    return d

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(320))
    city_id = db.Column(db.Integer, db.ForeignKey('City.id'),
        nullable=False)
    shows = db.relationship("Show", backref='venue', lazy=True)

    def get_venue(self):
      return {
        "id": self.id, 
        "name": self.name,
        "genres": self.genres.split(","),
        "address": self.address,
        "city": City.query.filter(City.id == self.city_id).first().name, 
        "state": self.state, 
        "phone": self.phone,
        "website": self.website,
        "facebook_link": self.facebook_link,
        "seeking_talent": self.seeking_talent,
        "seeking_description": self.seeking_description,
        "image_link": self.image_link,
        "past_shows": self.get_past_shows(),
        "upcoming_shows": self.get_upcoming_shows(),
        "past_shows_count": len(self.get_past_shows()),
        "upcoming_shows_count": len(self.get_upcoming_shows())
      }

    def get_upcoming_shows(self):
      return [item.venue_shows() for item in db.session.query(Show).filter(Show.venue_id == self.id).filter(Show.start_time >= datetime.today()).all()]

    def get_past_shows(self):
      return [item.venue_shows() for item in db.session.query(Show).filter(Show.venue_id == self.id).filter(Show.start_time < datetime.today()).all()]
    
    def show_venues(self):
      d = {
        "id": self.id,
        "name": self.name,
        "num_upcoming_shows": len(self.get_upcoming_shows())
      }
      return d




class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(320))
    shows = db.relationship("Show", backref='artist', lazy=True)


    def get_artist(self):
      return {
        "id": self.id, 
        "name": self.name,
        "genres": self.genres.split(","),
        "city": self.city, 
        "state": self.state, 
        "phone": self.phone,
        "website": self.website,
        "facebook_link": self.facebook_link,
        "seeking_venue": self.seeking_venue,
        "seeking_description": self.seeking_description,
        "image_link": self.image_link,
        "past_shows": self.get_past_shows(),
        "upcoming_shows": self.get_upcoming_shows(),
        "past_shows_count": len(self.get_past_shows()),
        "upcoming_shows_count": len(self.get_upcoming_shows())
      }

    def get_upcoming_shows(self):
      return [item.artist_shows() for item in db.session.query(Show).filter(Show.artist_id == self.id).filter(Show.start_time >= datetime.today()).all()]

    def get_past_shows(self):
      return [item.artist_shows() for item in db.session.query(Show).filter(Show.artist_id == self.id).filter(Show.start_time < datetime.today()).all()]


    def show_artists(self):
      d = {
        "id": self.id,
        "name": self.name,
        "num_upcoming_shows": len(self.get_upcoming_shows())
      }
      return d
    
        


class Show(db.Model):
  __tablename__ = "Show"
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),
        nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),
        nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  def venue_shows(self):
    artist = self.artist 
    return {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": self.start_time
    }

  def artist_shows(self):
    venue = self.venue 
    return {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": self.start_time
    }

  def make_show(self):
    d = {
      "venue_id": self.venue_id,
      "venue_name": self.venue.name,
      "artist_id": self.artist_id,
      "artist_name": self.artist.name,
      "artist_image_link": self.artist.image_link,
      "start_time": self.start_time
    }
    return d


# avoid recursive import 
from forms import *


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = [c.show_venue() for c in City.query.order_by(City.name).all() if c.show_venue() is not None]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  term = request.form.get("search_term", "")
  data = [item.show_venues() for item in Venue.query.filter(Venue.name.ilike(f"%{term}%")).all() if item.show_venues is not None]
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.filter(Venue.id == venue_id).first() 
  if data:
    data = data.get_venue()
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  venue = Venue() 
  has_error = False 
  try:
    venue.genres = ",".join(request.form.getlist("genres"))
    form = request.form.to_dict()
    venue.name = form.get("name")
    venue.address = form.get("address")
    venue.state = form.get("state")
    venue.phone = form.get("phone")
    venue.website = form.get("website")
    venue.facebook_link = form.get("facebook_link")
    venue.seeking_talent = form.get("seeking_talent", None)
    if venue.seeking_talent is None:
      venue.seeking_talent = False 
    else:
      venue.seeking_talent = True
    venue.seeking_description = form.get("seeking_description")
    venue.image_link = form.get("image_link")
    city = form.get("city", "")
    city_from_db = City.query.filter(City.name.ilike(f"{city.lower()}")).first() 
    if city_from_db is not None:
      venue.city_id = city_from_db.id
    else:
      c = City() 
      c.name = city
      c.state = form.get("state")
      db.session.add(c)
      db.session.commit() 
      venue.city_id = c.id
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    has_error = True 
  finally:
    db.session.close()
  
  if not has_error:
    flash(f"Venue {request.form['name']} was listed successfully!")
    return redirect(url_for("index"))
  else:
    flash(f"Error occured while saving Venue: {request.form['name']}. Venue could not be listed")
    return redirect(url_for("create_venue_form"))
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  id = None 
  try:
    id = int(venue_id)
  except:
    id = None
  if id is not None:
    venue = Venue.query.filter(Venue.id == id).first() 
    if venue is not None:
      db.session.delete(venue)
      db.session.commit()
      return jsonify({"success": True, "deleted": id})
  return jsonify({"success": False})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = [art.show_artists() for art in Artist.query.order_by(Artist.name).all()]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  term = request.form.get("search_term", "")
  data = [item.show_artists() for item in Artist.query.filter(Artist.name.ilike(f"%{term}%")).all()]
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.filter(Artist.id == artist_id).first() 
  if data:
    data = data.get_artist()
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter(Artist.id == artist_id).first() 
  if not artist:
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    genres = request.form.getlist("genres")
    form = request.form.to_dict() 
    artist.name = form.get("name")
    city = form.get("city", "")
    city_from_db = City.query.filter(City.name.ilike(f"{city.lower()}")).first() 
    if city_from_db is not None:
      artist.city = city_from_db.name
    else:
      c = City() 
      c.name = city
      c.state = form.get("state")
      db.session.add(c)
      db.session.commit() 
      artist.city = c.name
    artist.state = form.get("state")
    artist.phone = form.get("phone")
    artist.genres = ",".join(genres)
    artist.facebook_link = form.get("facebook_link")
    db.session.commit()
    return redirect(url_for("artists"))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first() 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.filter(Venue.id == venue_id).first()
  if not venue:
    return redirect(url_for('show_venue', venue_id=venue_id))
  if venue is not None:
    venue.genres = ",".join(request.form.getlist("genres"))
    form = request.form.to_dict()
    venue.name = form.get("name")
    venue.address = form.get("address")
    venue.state = form.get("state")
    venue.phone = form.get("phone")
    venue.facebook_link = form.get("facebook_link")
    city = form.get("city", "")
    city_from_db = City.query.filter(City.name.ilike(f"{city.lower()}")).first() 
    if city_from_db is not None:
      venue.city_id = city_from_db.id
    else:
      c = City() 
      c.name = city
      c.state = form.get("state")
      db.session.add(c)
      db.session.commit() 
      venue.city_id = c.id
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  artist = Artist() 
  has_error = False 
  try:
    artist.genres = ",".join(request.form.getlist("genres"))
    form = request.form.to_dict()
    artist.name = form.get("name")
    artist.state = form.get("state")
    artist.phone = form.get("phone")
    artist.website = form.get("website")
    artist.facebook_link = form.get("facebook_link")
    artist.seeking_venue = form.get("seeking_venue", None)
    if artist.seeking_venue is None:
      artist.seeking_venue = False 
    else:
      artist.seeking_venue = True
    artist.seeking_description = form.get("seeking_description")
    artist.image_link = form.get("image_link")
    city = form.get("city", "")
    city_from_db = City.query.filter(City.name.ilike(f"{city.lower()}")).first() 
    if city_from_db is not None:
      artist.city = city_from_db.name
    else:
      c = City() 
      c.name = city
      c.state = form.get("state")
      db.session.add(c)
      db.session.commit() 
      artist.city = c.name
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    has_error = True 
  finally:
    db.session.close()
  
  if not has_error:
    flash(f"Artist {request.form['name']} was listed successfully!")
    return redirect(url_for("index"))
  else:
    flash(f"Error occured while saving Artist: {request.form['name']}. Venue could not be listed")
    return redirect(url_for("create_artist_form"))

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = [item.make_show() for item in Show.query.order_by(Show.id).all()]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  show = Show() 
  has_error = False 
  try:
    form = request.form.to_dict() 
    show.artist_id = form.get("artist_id")
    show.venue_id = form.get("venue_id")
    show.start_time = form.get("start_time")
    db.session.add(show)
    db.session.commit()
  except:
    has_error = True
    db.session.rollback() 
  finally: 
    db.session.close() 
  if not has_error:
    flash('Show was successfully listed!')
    return redirect(url_for("index"))
  else:
    flash('An error occurred. Show could not be listed.')
    return redirect(url_for("create_shows"))
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
