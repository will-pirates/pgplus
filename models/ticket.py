import api

from google.appengine.ext import db

class Ticket(db.Model):
    location = db.GeoPtProperty()
    location_text = db.StringProperty()
    issue_type = db.StringProperty()
    equipment = db.StringProperty()
    services = db.StringProperty()
    notes = db.StringListProperty()
    documents = db.StringListProperty()
    name = db.StringProperty(indexed=False)
    note_id = db.StringProperty(indexed=False)
    assigned = db.BooleanProperty()