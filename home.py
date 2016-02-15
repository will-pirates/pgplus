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
    # joe's creds
    credentials = OAuth2Credentials.from_json('{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-15T08:24:55Z", "id_token": {"aud": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "IAGbKo5Yf6pplIpDcdghRA", "exp": 1455524695, "azp": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iat": 1455521095, "sub": "110209618710722590711"}, "access_token": "ya29.iQKgr-A57u_U4ULgSMUZpcFQ4oGe1bI74mja4nj4CpLuhbP7AxaNmBVwcHMwHoWq8k9t", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iQKgr-A57u_U4ULgSMUZpcFQ4oGe1bI74mja4nj4CpLuhbP7AxaNmBVwcHMwHoWq8k9t", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/m6mN-o5-tZG9so8vHJAyF6p0W5_msFtXaJwUfulv6bY", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjRjMTgxMzg4MGQ1NjM1Nzg3MTcxMGE0ODlhYWVhY2JkZTU4MGE3N2MifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IklBR2JLbzVZZjZwcGxJcERjZGdoUkEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTAyMDk2MTg3MTA3MjI1OTA3MTEiLCJhenAiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU1MjEwOTUsImV4cCI6MTQ1NTUyNDY5NX0.ipoBdvHVqaET8WWZ51-wRkiMOopjJmMLqNtcuRYtz84rOj2W-qN3LWL52lBISoPyhHYjN0yupFFlYgSrh35yHKEWdCkqJL0-vd-CDSKp8Ca4hC4eah3WUUis9rZ41EIIlrRFuCLmSYgRzv7fvXBReKa-hdEbhkH-9sdOTXOA38i6P8q1dctsJmh93MD6odfG6AGW1FgN4M7ZPaUZnIJLFb2hF0a7rm2AKROUGHRoe3wc8yCnHLTy8jDWL9TgNDC7UReiry2aGkQrXvveIhapVABjcy1lYdZ-k7N1NSzwZcqOxjwvXSj-e1zojsd0q-DoYySjwZ0MYqWTSHu5tqrp-A"}, "client_id": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "071WJgVZK-Rzb7bHyoHn28ao", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/m6mN-o5-tZG9so8vHJAyF6p0W5_msFtXaJwUfulv6bY", "user_agent": null}')
    
    # ranju's creds
    # credentials = OAuth2Credentials.from_json('{"user_agent": null, "access_token": "ya29.hgLC-ipSDIJ5kpEntB5LBpHhItUoeF2uChvRIKrY371fyVvgIpnIRIl-I2NPGpfNDLqs", "token_expiry": "2016-02-12T12:35:37Z", "scopes": ["https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.read", "https://www.googleapis.com/auth/plus.me"], "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "invalid": false, "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "refresh_token": "1/Ecq-WjOjv8MHaHTGttxWTrAGXxaIJk044PuNSKF75MxIgOrJDtdun6zK6XiATCKT", "token_uri": "https://accounts.google.com/o/oauth2/token", "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_response": {"token_type": "Bearer", "refresh_token": "1/Ecq-WjOjv8MHaHTGttxWTrAGXxaIJk044PuNSKF75MxIgOrJDtdun6zK6XiATCKT", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImE0MTYzNjE5NDIzZGNkM2E3MzYxYWNmMmE2NDFiZjZmN2M5ZTQ4OGEifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6ImZqd1RhbF9tN1J5bVVqazY1TnlZUVEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTA5MzI2ODYyNjQyMzgwNzMxMDQiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTUyNzY5MzYsImV4cCI6MTQ1NTI4MDUzNn0.CIp7kSf5G_TsDaSzZBWTB8jRZOLZizJq4YGbXM_KYeA1JFf3iWFN53Ifk6hUNw1X6A6nl_BVoe4lqWK9eXneGmTIABTpNSWHam9ZXW8b6JpAJVvoUjlQNBKwbVI5dXSd6UdWZCJ6VS8btVI9NjzTNTCvroa3LeNycYPfugZ-NmdTfcm7cEJ7LPN2hfcuDhWU_sZ5xNNzzcEEz3w_7zAQTfIoX1Ufi81o1PzLvlHp5hxyEle-kepbC6XTd4ZekbJBO6DafGQCU6fwNuNRnJFr0HuEbxMrcqMvVCa6yVjezIta0NvKFC2SjADTR6yTCYUFH1hIspC2NYh6_5hWGJdBjQ", "access_token": "ya29.hgLC-ipSDIJ5kpEntB5LBpHhItUoeF2uChvRIKrY371fyVvgIpnIRIl-I2NPGpfNDLqs", "expires_in": 3600}, "id_token": {"azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455276936, "exp": 1455280536, "sub": "110932686264238073104", "at_hash": "fjwTal_m7RymUjk65NyYQQ", "iss": "accounts.google.com"}, "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "_module": "oauth2client.client"}')
    
    # vvvv ashray's creds, don't upoad to appengine vvvv
    # credentials = OAuth2Credentials.from_json('{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-15T07:07:40Z", "id_token": {"aud": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "CQblAMCAH9O0ZNYAxG1zZA", "exp": 1455520059, "azp": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iat": 1455516459, "sub": "106258495568677784165"}, "access_token": "ya29.iQKHPJJyuIkGIfVAf1qwNEDwINXElO_H5XtWEBq_GBKLB87PmcH_qF1EhQgIhEBZRBZ2", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iQKHPJJyuIkGIfVAf1qwNEDwINXElO_H5XtWEBq_GBKLB87PmcH_qF1EhQgIhEBZRBZ2", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/fxyAKw-rmpmHD9AEsJrC-9NP7Tt_aHI4-M028GwYvNBIgOrJDtdun6zK6XiATCKT", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjRjMTgxMzg4MGQ1NjM1Nzg3MTcxMGE0ODlhYWVhY2JkZTU4MGE3N2MifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IkNRYmxBTUNBSDlPMFpOWUF4RzF6WkEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDYyNTg0OTU1Njg2Nzc3ODQxNjUiLCJhenAiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU1MTY0NTksImV4cCI6MTQ1NTUyMDA1OX0.dRmPcE-lfGvue1CTYZQbDfQe8-fsScEt22BWU0D6equmlNxddpRyAkl0tf68T4YTBgQ6qDJa5-ebJDZN3Qx7fU7IYop49egzvYDJK0p-rQKO8pIPnmKMVJYRwKtY9hQtX8h32smsvoZMeLfpyf1Xwzn7lpgY39f9w8hQ2PTgowbKfUAb9pkEByQs5p-4gb_WAvsr4bygqV2mhj-y0PbOET15kG003Oz4_O_tgqX8pFFEQxEY_8VVDhs_tZ0D66s07smBwZ6WJC8cCFLV-epi2EMYhEL4gkFVFU7Aaj0ZDlRRNzIs71C_gjj-dx-G8p9bPrg14BPtBxpz8zSBuGyu2A"}, "client_id": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "071WJgVZK-Rzb7bHyoHn28ao", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/fxyAKw-rmpmHD9AEsJrC-9NP7Tt_aHI4-M028GwYvNBIgOrJDtdun6zK6XiATCKT", "user_agent": null}')
    
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
    def read_note(self, note_id):
        credentials = refresh_token()
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('plusDomains', 'v1', http=http)
        activities_service = service.activities()
        activity = activities_service.get(activityId=note_id).execute()
        return activity.get('object').get('originalContent')

    def get(self):
        t = Ticket.all().filter('assigned', False).get()
        if t:
            t.assigned = True
            t.put()
            notes = []
            for note_id in t.note_ids:
                notes.append(self.read_note(note_id))
            self.response.write(json.dumps({'documents': [document.split(' :: ') for document in t.documents] , 'location_text': t.location_text, 'location': str(t.location), 'issue_type': t.issue_type, 'equipments': t.equipments, 'services': t.services, 'notes': notes}))


class CreateTicketHandler(webapp2.RequestHandler):
    def build_service(self):
        credentials = refresh_token()
        http = httplib2.Http()
        http = credentials.authorize(http)
        return build('plusDomains', 'v1', http=http)

    def create_circle(self):
        name = str(uuid.uuid4())
        new_circle = {
            'displayName': name
        }
        resp = self.service.circles().insert(userId = 'me', body = new_circle).execute()
        return resp['id']

    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'create_ticket.html')
        self.response.out.write(template.render(path, {}))

    def create_ticket(self, note_ids, circle_id, assigned=False):
        lat = self.request.get('lat')
        lng = self.request.get('lng')
        issue_type = self.request.get('issue-type')
        equipments = self.request.get('equipments').split('#$#')
        services = self.request.get('services').split('#$#')
        location = GeoPt(lat, lng)
        location_text = self.request.get('location_text')
        documents = self.request.get('documents').split('#$#')
        Ticket(documents=documents, note_ids=note_ids, circle_id=circle_id, location=location, location_text=location_text, assigned=assigned, issue_type=issue_type, equipments=equipments, services=services).put()

    def add_to_circle(self, user_id, circle_id):
        add_service = self.service.circles().addPeople(circleId=circle_id, userId=user_id)
        add_service.execute()

    def create_note(self, note):
        body = {"object": {"originalContent": note, "objectType": "note"}, "access": {"domainRestricted": True}}
        activity_service = self.service.activities().insert(userId='me', body=body)
        return activity_service.execute()['id']

    def post(self):
        self.service = self.build_service()
        dispatcher = self.request.get('dispatcher')
        other_engineers = self.request.get('other_engineers').split('#$#')
        notes = self.request.get('notes').split('#$#')
        note_ids = []
        for note in notes:
            note_ids.append(self.create_note(note))
        circle_id = self.create_circle()
        engineer = self.request.get('engineer')
        self.create_ticket(note_ids, circle_id)
        self.add_to_circle(engineer, circle_id)
        self.add_to_circle(dispatcher, circle_id)
        for other_engineer in other_engineers:
            self.add_to_circle(other_engineer, circle_id)

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