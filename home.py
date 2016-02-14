import os
import sys
import json
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import uuid
import webapp2
import httplib2
from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials

from google.appengine.ext.webapp import template

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials

# from api import get_credentials

from models.ticket import Ticket
from google.appengine.ext.db import GeoPt

def refresh_token():
    credentials = OAuth2Credentials.from_json('{"user_agent": null, "access_token": "ya29.hgLC-ipSDIJ5kpEntB5LBpHhItUoeF2uChvRIKrY371fyVvgIpnIRIl-I2NPGpfNDLqs", "token_expiry": "2016-02-12T12:35:37Z", "scopes": ["https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.read", "https://www.googleapis.com/auth/plus.me"], "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "invalid": false, "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "refresh_token": "1/Ecq-WjOjv8MHaHTGttxWTrAGXxaIJk044PuNSKF75MxIgOrJDtdun6zK6XiATCKT", "token_uri": "https://accounts.google.com/o/oauth2/token", "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_response": {"token_type": "Bearer", "refresh_token": "1/Ecq-WjOjv8MHaHTGttxWTrAGXxaIJk044PuNSKF75MxIgOrJDtdun6zK6XiATCKT", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImE0MTYzNjE5NDIzZGNkM2E3MzYxYWNmMmE2NDFiZjZmN2M5ZTQ4OGEifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6ImZqd1RhbF9tN1J5bVVqazY1TnlZUVEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTA5MzI2ODYyNjQyMzgwNzMxMDQiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTUyNzY5MzYsImV4cCI6MTQ1NTI4MDUzNn0.CIp7kSf5G_TsDaSzZBWTB8jRZOLZizJq4YGbXM_KYeA1JFf3iWFN53Ifk6hUNw1X6A6nl_BVoe4lqWK9eXneGmTIABTpNSWHam9ZXW8b6JpAJVvoUjlQNBKwbVI5dXSd6UdWZCJ6VS8btVI9NjzTNTCvroa3LeNycYPfugZ-NmdTfcm7cEJ7LPN2hfcuDhWU_sZ5xNNzzcEEz3w_7zAQTfIoX1Ufi81o1PzLvlHp5hxyEle-kepbC6XTd4ZekbJBO6DafGQCU6fwNuNRnJFr0HuEbxMrcqMvVCa6yVjezIta0NvKFC2SjADTR6yTCYUFH1hIspC2NYh6_5hWGJdBjQ", "access_token": "ya29.hgLC-ipSDIJ5kpEntB5LBpHhItUoeF2uChvRIKrY371fyVvgIpnIRIl-I2NPGpfNDLqs", "expires_in": 3600}, "id_token": {"azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455276936, "exp": 1455280536, "sub": "110932686264238073104", "at_hash": "fjwTal_m7RymUjk65NyYQQ", "iss": "accounts.google.com"}, "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "_module": "oauth2client.client"}')
    # vvvv ashray's creds, don't upoad to appengine vvvv
    # credentials = OAuth2Credentials.from_json('{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-14T14:23:28Z", "id_token": {"aud": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "FBp_XDHt2pRmreA6rVQCUg", "exp": 1455459814, "azp": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iat": 1455456214, "sub": "106258495568677784165"}, "access_token": "ya29.iAIqcllqhQZd78Tx5_FBbstAH2IWwqpM_2x0o9He0Y0XkhA1QjU6faYU_1ygr3tYDGcdXQ", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iAIqcllqhQZd78Tx5_FBbstAH2IWwqpM_2x0o9He0Y0XkhA1QjU6faYU_1ygr3tYDGcdXQ", "token_type": "Bearer", "expires_in": 3592, "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjA4MDgyOWI4MmU0MGZjNzIzM2FhMmM0YjViOTFjNzU2NDc1MThhNzkifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IkZCcF9YREh0MnBSbXJlQTZyVlFDVWciLCJhdWQiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDYyNTg0OTU1Njg2Nzc3ODQxNjUiLCJhenAiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU0NTYyMTQsImV4cCI6MTQ1NTQ1OTgxNH0.VtYVZ_KwYOLeYiuELvAWtIv58tzCJD95HcRlMZYI4qUii0k9exQPz-ZA1BF2Fx1jN_mw2GoL2OW3k2Dji8ySh7Ez5FRRVNCug6n2lyUMq8kluRMEGyOy14HM-QQNsYHFu_CnHFZ8mENUiksKy6LoXrJktH3pTROsZBgmTor7XsdpvLwrW9S9ffkWvyCQGJeM5sr_qpqg--VDzNWXbp46bGfc6dCPvkeAmzbtAlzYLQKEKgXfPs8yG90Z23c6B5dv78gjwlAic2PfadPrTSYqwyOl3tSYHeUSEu-MhrD7ugOD2DQeTwnGLattBhF0bpaqeN8V5tGuzDpOmSzREcqe_A"}, "client_id": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "071WJgVZK-Rzb7bHyoHn28ao", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": null, "user_agent": null}')
    
    credentials.refresh(httplib2.Http())
    return credentials

class MainPage(webapp2.RequestHandler):
    def get(self):
        '''
        uri = get_credentials()
        self.redirect(uri)
        '''
        credentials = OAuth2Credentials.from_json('{"user_agent": null, "access_token": "ya29.hgLC-ipSDIJ5kpEntB5LBpHhItUoeF2uChvRIKrY371fyVvgIpnIRIl-I2NPGpfNDLqs", "token_expiry": "2016-02-12T12:35:37Z", "scopes": ["https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.read", "https://www.googleapis.com/auth/plus.me"], "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "invalid": false, "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "refresh_token": "1/Ecq-WjOjv8MHaHTGttxWTrAGXxaIJk044PuNSKF75MxIgOrJDtdun6zK6XiATCKT", "token_uri": "https://accounts.google.com/o/oauth2/token", "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_response": {"token_type": "Bearer", "refresh_token": "1/Ecq-WjOjv8MHaHTGttxWTrAGXxaIJk044PuNSKF75MxIgOrJDtdun6zK6XiATCKT", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImE0MTYzNjE5NDIzZGNkM2E3MzYxYWNmMmE2NDFiZjZmN2M5ZTQ4OGEifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6ImZqd1RhbF9tN1J5bVVqazY1TnlZUVEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTA5MzI2ODYyNjQyMzgwNzMxMDQiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTUyNzY5MzYsImV4cCI6MTQ1NTI4MDUzNn0.CIp7kSf5G_TsDaSzZBWTB8jRZOLZizJq4YGbXM_KYeA1JFf3iWFN53Ifk6hUNw1X6A6nl_BVoe4lqWK9eXneGmTIABTpNSWHam9ZXW8b6JpAJVvoUjlQNBKwbVI5dXSd6UdWZCJ6VS8btVI9NjzTNTCvroa3LeNycYPfugZ-NmdTfcm7cEJ7LPN2hfcuDhWU_sZ5xNNzzcEEz3w_7zAQTfIoX1Ufi81o1PzLvlHp5hxyEle-kepbC6XTd4ZekbJBO6DafGQCU6fwNuNRnJFr0HuEbxMrcqMvVCa6yVjezIta0NvKFC2SjADTR6yTCYUFH1hIspC2NYh6_5hWGJdBjQ", "access_token": "ya29.hgLC-ipSDIJ5kpEntB5LBpHhItUoeF2uChvRIKrY371fyVvgIpnIRIl-I2NPGpfNDLqs", "expires_in": 3600}, "id_token": {"azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455276936, "exp": 1455280536, "sub": "110932686264238073104", "at_hash": "fjwTal_m7RymUjk65NyYQQ", "iss": "accounts.google.com"}, "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "_module": "oauth2client.client"}')
        credentials.refresh(httplib2.Http())

        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('plusDomains', 'v1', http=http)

        new_circle = {
            'displayName': 'Flair Club'
        }
        resp = service.circles().insert(userId = 'me', body = new_circle).execute()
        print(resp)

class AuthHandler(webapp2.RequestHandler):
    def get(self):
        '''
        SCOPES = ['https://www.googleapis.com/auth/plus.me',
              'https://www.googleapis.com/auth/plus.stream.write',
              'https://www.googleapis.com/auth/plus.stream.read',
              'https://www.googleapis.com/auth/plus.circles.write',
              'https://www.googleapis.com/auth/plus.circles.read']

        REDIRECT_URI = 'http://oscarosl-test.appspot.com/auth'

        CLIENT_ID = '255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com'
        CLIENT_SECRET = '1kk1vYbu8hKBz_GxYjJl6Frm'

        flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                               client_secret=CLIENT_SECRET,
                               scope=SCOPES,
                               redirect_uri=REDIRECT_URI)
        code = self.request.get('code')
        credentials = flow.step2_exchange(code)

        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('plusDomains', 'v1', http=http)

        new_circle = {
            'displayName': 'MWC Test',
            'description': 'MWC description'
        }
        #service.circles().insert(userId = 'me', body = new_circle).execute()
        print(credentials.to_json())
        '''
        credentials = OAuth2Credentials.from_json('{"user_agent": null, "access_token": "ya29.hgLC-ipSDIJ5kpEntB5LBpHhItUoeF2uChvRIKrY371fyVvgIpnIRIl-I2NPGpfNDLqs", "token_expiry": "2016-02-12T12:35:37Z", "scopes": ["https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.read", "https://www.googleapis.com/auth/plus.me"], "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "invalid": false, "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "refresh_token": "1/Ecq-WjOjv8MHaHTGttxWTrAGXxaIJk044PuNSKF75MxIgOrJDtdun6zK6XiATCKT", "token_uri": "https://accounts.google.com/o/oauth2/token", "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_response": {"token_type": "Bearer", "refresh_token": "1/Ecq-WjOjv8MHaHTGttxWTrAGXxaIJk044PuNSKF75MxIgOrJDtdun6zK6XiATCKT", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImE0MTYzNjE5NDIzZGNkM2E3MzYxYWNmMmE2NDFiZjZmN2M5ZTQ4OGEifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6ImZqd1RhbF9tN1J5bVVqazY1TnlZUVEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTA5MzI2ODYyNjQyMzgwNzMxMDQiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTUyNzY5MzYsImV4cCI6MTQ1NTI4MDUzNn0.CIp7kSf5G_TsDaSzZBWTB8jRZOLZizJq4YGbXM_KYeA1JFf3iWFN53Ifk6hUNw1X6A6nl_BVoe4lqWK9eXneGmTIABTpNSWHam9ZXW8b6JpAJVvoUjlQNBKwbVI5dXSd6UdWZCJ6VS8btVI9NjzTNTCvroa3LeNycYPfugZ-NmdTfcm7cEJ7LPN2hfcuDhWU_sZ5xNNzzcEEz3w_7zAQTfIoX1Ufi81o1PzLvlHp5hxyEle-kepbC6XTd4ZekbJBO6DafGQCU6fwNuNRnJFr0HuEbxMrcqMvVCa6yVjezIta0NvKFC2SjADTR6yTCYUFH1hIspC2NYh6_5hWGJdBjQ", "access_token": "ya29.hgLC-ipSDIJ5kpEntB5LBpHhItUoeF2uChvRIKrY371fyVvgIpnIRIl-I2NPGpfNDLqs", "expires_in": 3600}, "id_token": {"azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455276936, "exp": 1455280536, "sub": "110932686264238073104", "at_hash": "fjwTal_m7RymUjk65NyYQQ", "iss": "accounts.google.com"}, "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "_module": "oauth2client.client"}')
        print(credentials.to_json())
        print('------')
        credentials.refresh(httplib2.Http())
        print(credentials.to_json())


class GetTicketHandler(webapp2.RequestHandler):
    def get(self):
        t = Ticket.all().filter('assigned', False).get()
        if t:
            t.assigned = True
            t.put()
            self.response.write(json.dumps({'documents': t.documents , 'location_text': t.location_text, 'location': str(t.location), 'issue_type': t.issue_type, 'equipment': t.equipment, 'services': t.services}))


class CreateTicketHandler(webapp2.RequestHandler):
    def create_circle(self):
        name = str(uuid.uuid4())
        credentials = refresh_token()
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('plusDomains', 'v1', http=http)
        new_circle = {
            'displayName': name
        }
        resp = service.circles().insert(userId = 'me', body = new_circle).execute()
        return resp['id']
        # resp = '1'
        # ticket = Ticket(key_name=resp['id'], name=name, assigned=assigned)
        # ticket.location = self.request.get('location')
        # ticket.issue_type = self.request.get('issue_type')
        # ticket.equipment = self.request.get('equipment')
        # ticket.services = self.request.get('services')
        # ticket.notes = [self.request.get('notes')]
        # ticket.documents = [self.request.get('documents')]
        # ticket.put()

    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'create_ticket.html')
        self.response.out.write(template.render(path, {}))

    def create_ticket(self, note_id, circle_id, assigned=False):
        lat = self.request.get('lat')
        lng = self.request.get('lng')
        issue_type = self.request.get('issue-type')
        equipment = self.request.get('equipment')
        services = self.request.get('services')
        location = GeoPt(lat, lng)
        location_text = self.request.get('location_text')
        documents = self.request.get('documents').split(';')
        Ticket(documents=documents, note_id=note_id, circle_id=circle_id, location=location, location_text=location_text, assigned=assigned, issue_type=issue_type, equipment=equipment, services=services).put()

    def add_to_circle(self, user_id, circle_id):
        logging.info(user_id)
        logging.info(circle_id)
        credentials = refresh_token()
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('plusDomains', 'v1', http=http)
        add_service = service.circles().addPeople(circleId=circle_id, userId=user_id)
        add_service.execute()

    def create_note(self):
        credentials = refresh_token()
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('plusDomains', 'v1', http=http)
        body = {"object": {"originalContent": self.request.get('notes'), "objectType": "note"}, "access": {"domainRestricted": True}}
        activity_service = service.activities().insert(userId='me', body=body)
        return activity_service.execute()['id']

    def post(self):
        note_id = self.create_note()
        logging.info('note created')
        circle_id = self.create_circle()
        logging.info('circle created')
        assignee = self.request.get('assignee')
        self.create_ticket(note_id, circle_id)
        self.add_to_circle(assignee, circle_id)


class AssignCirclesHandler(webapp2.RequestHandler):
    def get(self):
        circle = Circle.all().filter('assigned', False).get()
        circle.assigned = True
        circle.put()
        response = {'id': circle.key().name(), 'name': circle.name}
        self.response.write(response)


class GetCirclesHandler(webapp2.RequestHandler):
    def get_circles(self, user_id='me'):
        credentials = refresh_token()
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('plusDomains', 'v1', http=http)
        circle_service = service.circles()
        request = circle_service.list(userId=user_id)
        circle_list = request.execute()
        return circle_list

    def get(self):
        self.response.write(self.get_circles())


class CreateNoteHandler(webapp2.RequestHandler):
    def get(self):
        circles = [(circle.key().name(), circle.name) for circle in Circle.all()]
        path = os.path.join(os.path.dirname(__file__), 'notes.html')
        self.response.out.write(template.render(path, {'circles': circles}))

    def post(self):
        content = self.request.get('content')
        id = self.request.get('id')
        circle = Circle.get_by_key_name(id)
        note = api.create_note(content)
        circle.note_id = note['id']
        circle.put()

class GetNotesHandler(webapp2.RequestHandler):
    def get(self):
        circles = Circle.all()
        data = []
        for circle in circles:
            data.append({'circle': api.get_circle(circle.key().name()), 'note': api.get_activity(circle.note_id)})
        # circles = api.get_circle(circle.key().name())
        # notes = api.get_activity(circle.note_id)
        # notes = api.get_activities()
        # circles = api.get_circles()
        path = os.path.join(os.path.dirname(__file__), 'list.html')
        self.response.out.write(template.render(path, {'data': data}))

app = webapp2.WSGIApplication([
                                ('/', MainPage),
                                ('/auth', AuthHandler),
                                ('/tickets/create', CreateTicketHandler),
                                ('/tickets/get', GetTicketHandler),
                                ('/circles/get', GetCirclesHandler),
                                ('/circles/assign', AssignCirclesHandler),
                                ('/notes/create', CreateNoteHandler),
                                ('/notes/get', GetNotesHandler)
                            ], debug=True)