from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

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
    shows = db.relationship("Show", backref="Venue")

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
    
    #implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship("Show", backref="Artist")



class Show(db.Model):
  __tablename__ = "Show"

  id = db.Column(db.Integer, primary_key=True)
  artist_id=db.Column(db.Integer , db.ForeignKey("Artist.id"))
  venue_id=db.Column(db.Integer, db.ForeignKey("Venue.id"))
  start_time=db.Column(db.DateTime)

#Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

  artistFK = db.relationship("Artist", foreign_keys=[artist_id])
  venueFK = db.relationship("Venue", foreign_keys=[venue_id])