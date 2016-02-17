import api

from google.appengine.ext import db

class Ticket(db.Model):
    location = db.GeoPtProperty()
    location_text = db.StringProperty()
    issue_type = db.StringProperty()
    equipments = db.StringListProperty()
    services = db.StringListProperty()
    notes = db.StringListProperty()
    document_ids = db.StringListProperty()
    name = db.StringProperty(indexed=False)
    note_ids = db.StringListProperty()
    circle_id = db.StringProperty(indexed=False)
    assigned = db.BooleanProperty()
    engineer = db.StringListProperty()
    customer = db.StringListProperty()

class LastAssignedTicket(db.Model):
    ticket = db.ReferenceProperty()