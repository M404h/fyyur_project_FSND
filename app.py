#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, exception
from flask_wtf import Form
from sqlalchemy.orm import backref
from forms import *
from flask_migrate import Migrate
from sqlalchemy.orm import relationship, backref

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connecte to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres=db.Column(db.String())
    web_link = db.Column(db.String(120))
    looking_for_talent=db.Column(db.Boolean(), default=False)
    seeking_description=db.Column(db.String())

    shows = db.relationship("Show", backref="Venue",lazy=True)

    #implemented any missing fields, as a database migration using Flask-Migrate


      
class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    web_link = db.Column(db.String(120))
    looking_for_venues=db.Column(db.Boolean(), default=False)
    seeking_description=db.Column(db.String())
    
    shows = db.relationship("Show", backref="Artist",lazy=True)

    #implement any missing fields, as a database migration using Flask-Migrate



class Show(db.Model):
  __tablename__ = "Show"

  id = db.Column(db.Integer, primary_key=True)
  artist_id=db.Column(db.Integer , db.ForeignKey("Artist.id"))
  venue_id=db.Column(db.Integer, db.ForeignKey("Venue.id"))
  start_time=db.Column(db.DateTime)

#Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

  artistFK = db.relationship("Artist", backref="Artist",lazy=True)
  venueFK = db.relationship("Venue", backref="Venue",lazy=True)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.

  data=[]
  city_query=Venue.query.with_entities(Venue.city, Venue.state).distinct().all()

  for c in city_query:

    venues = Venue.query.filter(Venue.city == c.city).filter(Venue.state == c.state)
    venues_array=[]

    for v in venues:
      new_shows_num=Show.query.filter(Venue.id==v.id).filter(Show.start_time >= datetime.now()).count()
      if new_shows_num<0:
        new_shows_num=0;

      venues_array.append({
      "id": v.id,
      "name": v.name,
      "num_upcoming_shows":new_shows_num
      })


    data.append({
      "city": c.city,
      "state": c.state,
      "venues": venues_array,
      })

   
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues(): # not working 
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get("search_term")
  venue_data = Venue.query.filter(Venue.name.ilike('%' + search_term+ '%')).all()
  venues_results_array=[]
  for v in venue_data:
    show_num = Show.query.filter(Show.venue_id == v.id).filter(Show.start_time>=datetime.now()).count()
    venues_results_array.append({
        "id": v.id,
        "name": v.name,
        "num_upcoming_show": show_num
      })
  
  #test upcoming shows query
  #for ven in venues_results_array:
  #  print(ven)    
  
  response = {
    "count": len(venues_results_array),
    "data": venues_results_array
  }


  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id

  data =[]

  show_query = Show.query.filter(Show.venue_id == venue_id).all()
  v = Venue.query.filter(Venue.id == venue_id).first()

  upcoming_shows = []
  past_shows = []

  genresList =v.genres.strip('}{').split(',');
  

  for s in show_query:
    
    show_object={
      "artist_id": s.Artist.id,
      "artist_name":s.Artist.name,
      "artist_image_link": s.Artist.image_link,
      "start_time":s.start_time.ctime() 
    }

    if s.start_time >= datetime.now(): 
      upcoming_shows.append(show_object)
    else:
      past_shows.append(show_object)


  data={
    "id": venue_id,
    "name": v.name,
    "genres": genresList,
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": v.web_link,
    "facebook_link": v.facebook_link,
    "seeking_talent": v.looking_for_talent,
    "seeking_description": v.seeking_description,
    "image_link": v.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion

  try:
    seeking_talent_value=request.form.get('seeking_talent')
    seeking_talent=False
    if seeking_talent_value =='y':
      seeking_talent=True

    venue = Venue(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      address=request.form['address'],
      phone=request.form['phone'],
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'],
      genres=request.form.getlist('genres'),
      web_link= request.form['website_link'], 
      looking_for_talent=seeking_talent,
      seeking_description=request.form['seeking_description']
      )
    db.session.add(venue)
    db.session.commit()      
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()
  
  
  # on successful db insert, flash success
  # on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:

    Venue.query.filter_by(Venue.id ==venue_id).delete()
    db.session.commit()      
    flash('Venue was deleted successfully')

  except:
    db.session.rollback()
    flash('An error occured. Venue could not be deleted.')

  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # replace with real data returned from querying the database
  data=[]
  artist_query = Artist.query.with_entities(Artist.id,Artist.name).all()
  for a in artist_query:
       data.append({
        "id": a.id,
        "name": a.name
      })
      
  return render_template('pages/artists.html', artists=data)



@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get("search_term")
  artist_data = Artist.query.filter(Artist.name.ilike('%' + search_term+ '%')).all()
  artist_results_array=[]
  for a in artist_data:
    show_num = Show.query.filter(Show.artist_id == a.id).filter(Show.start_time>=datetime.now()).count()
    artist_results_array.append({
        "id": a.id,
        "name": a.name,
        "num_upcoming_show": show_num
      })

  response = {
    "count": len(artist_results_array),
    "data": artist_results_array
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # replace with real artist data from the artist table, using artist_id
    data =[]

    show_query = Show.query.filter(Show.artist_id == artist_id).all()
    a = Artist.query.filter(Artist.id == artist_id).first()

    upcoming_shows = []
    past_shows = []

    genresList =a.genres.strip('}{').split(',');
    
    for s in show_query:
      
      show_object={
      "venue_id": s.Venue.id,
      "venue_name": s.Venue.name,
      "venue_image_link": s.Venue.image_link,
      "start_time": s.start_time.ctime(),
      }

      if s.start_time >= datetime.now(): 
        upcoming_shows.append(show_object)
      else:
        past_shows.append(show_object)
    
    data={
    "id": artist_id,
    "name": a.name,
    "genres": genresList,
    "city": a.city,
    "state": a.state,
    "phone": a.phone,
    "website": a.web_link,
    "facebook_link": a.facebook_link,
    "seeking_venue": a.looking_for_venues,
    "seeking_description":a.seeking_description,
    "image_link": a.image_link,
    "past_shows":past_shows ,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.web_link
  form.seeking_venue.data = artist.looking_for_venues
  form.seeking_description.data = artist.seeking_description

  
  # populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  try:

    artist = Artist.query.get(artist_id)

    looking_for_venues_value=request.form.get('seeking_venue')
    looking_for_venues=False
    if looking_for_venues_value =='y':
      looking_for_venues=True

    artist.name=request.form['name']
    artist.city=request.form['city']
    artist.state=request.form['state']
    artist.phone=request.form['phone']
    artist.genres=request.form.getlist('genres')
    artist.image_link=request.form['image_link']
    artist.facebook_link=request.form['facebook_link']
    artist.web_link= request.form['website_link']
    artist.looking_for_venues=looking_for_venues
    artist.seeking_description=request.form['seeking_description']
      
    db.session.commit()      
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  except:
    db.session.rollback()
    flash('An error occured. Artist ' + request.form['name'] + ' could not be updated.')

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.web_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.looking_for_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link


  # populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:

    venue = Venue.query.get(venue_id)

    seeking_talent_value=request.form.get('seeking_talent')
    seeking_talent=False
    if seeking_talent_value =='y':
      seeking_talent=True

    
    venue.name=request.form['name']
    venue.city=request.form['city']
    venue.state=request.form['state']
    venue.address=request.form['address']
    venue.phone=request.form['phone']
    venue.image_link=request.form['image_link']
    venue.facebook_link=request.form['facebook_link']
    venue.genres=request.form.getlist('genres')
    venue.web_link= request.form['website_link']
    venue.looking_for_talent=seeking_talent
    venue.seeking_description=request.form['seeking_description']
      
    db.session.commit()      
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  except:
    db.session.rollback()
    flash('An error occured. Venue ' + request.form['name'] + ' could not be updated.')

  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion

  try:
    looking_for_venues_value=request.form.get('seeking_venue')
    looking_for_venues=False
    if looking_for_venues_value =='y':
      looking_for_venues=True

    artist = Artist(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'],
      web_link= request.form['website_link'], 
      looking_for_venues=looking_for_venues,
      seeking_description=request.form['seeking_description']
      )
    db.session.add(artist)
    db.session.commit()      
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occured. Artist ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()

  # on successful db insert, flash success
  # on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # replace with real venues data.
  #num_shows should be aggregated based on number of upcoming shows per venue.
  data=[] 
  show_query=Show.query.all() 

  for s in show_query:
    data.append({
      "venue_id":s.Venue.id,
      "venue_name":s.Venue.name,
      "artist_id":s.Artist.id,
      "artist_name":s.Artist.name,
      "artist_image_link":s.Artist.image_link,
      "start_time":s.start_time.ctime()
    })
   
   
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db, instead

  try:

    show = Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time'],
      )
    db.session.add(show)
    db.session.commit()      
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')

  finally:
    db.session.close()

  # on successful db insert, flash success
  # on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
