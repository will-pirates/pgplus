import api

class Ticket(object):
	def __init__(self, type, price_range, customer, location):
		self.type = type
		self.price_range = price_range
		self.customer = customer
		self.location = location
		self.circle = None
		self.note = None

	def create_circle(self, name, description):
		self.circle = api.create_circle(name, description)

	def create_note(self, content):
		self.note = api.create_note(content)