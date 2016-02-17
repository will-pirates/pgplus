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

people = {'customers':[['Rick','103764585826277201640'], ['Robert','108560908635605545932'], ['Ryan','102345940077083980832'],['Rachel','107612119418245526899'],['Rose','108612246962932756480']],
          'engineers':[['Joe','110257721827374623737'],['Josephine','117685299168782698970'],['Jeremy','101967792556257735208'],['Jhon','103387629180365578874'],['James','101447084593147265288'],['Jenny','102417683683083682579'],['Jeff','115781491509522514753'],['Jason','105193078925726528104'],['Jenna','109061817072269062716']],
          'experts':[['TWC','112739138406530779564'],['Cisco','110132770680215220078'],['Verizon','108741317245837764468'],['Belkin','112043759976089842597'],['Apple','103675625919779944270'],['Netgear','118014758899268715696']]}

tags = ['broadband', 'hvac', 'plumbing', 'home security']

tags_to_people = {'broadband': {'experts': [['Netgear', '118014758899268715696'], ['Apple', '103675625919779944270']], 'engineers': [['Jhon', '103387629180365578874'], ['Joe', '110257721827374623737'], ['Jenna', '109061817072269062716']]}, 'plumbing': {'experts': [['TWC', '112739138406530779564'], ['Belkin', '112043759976089842597']], 'engineers': [['Josephine', '117685299168782698970']]}, 'home security': {'engineers': [['James', '101447084593147265288'], ['Jason', '105193078925726528104']]}, 'hvac': {'experts': [['Verizon', '108741317245837764468'], ['Cisco', '110132770680215220078']], 'engineers': [['Jeremy', '101967792556257735208'], ['Jeff', '115781491509522514753'], ['Jenny', '102417683683083682579']]}}

id_to_name = {'103387629180365578874': 'Jhon', '118014758899268715696': 'Netgear', '101967792556257735208': 'Jeremy', '110132770680215220078': 'Cisco', '117685299168782698970': 'Josephine', '112739138406530779564': 'TWC', '115781491509522514753': 'Jeff', '102417683683083682579': 'Jenny', '110257721827374623737': 'Joe', '112043759976089842597': 'Belkin', '103675625919779944270': 'Apple', '109061817072269062716': 'Jenna', '108741317245837764468': 'Verizon', '101447084593147265288': 'James', '105193078925726528104': 'Jason'}

def refresh_token():
    # peggy's creds
    credentials = OAuth2Credentials.from_json('{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-16T11:19:50Z", "id_token": {"aud": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "PNjLEZCSbweplyXSCkJtiw", "exp": 1455621590, "azp": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iat": 1455617990, "sub": "108477436847495384050"}, "access_token": "ya29.igLy8L3IGaYFaht5K8sxDWBhcw_zyajnkNvcrWeOgAarX7GI97zZYgbQfjbUlmQP-hKJ", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.igLy8L3IGaYFaht5K8sxDWBhcw_zyajnkNvcrWeOgAarX7GI97zZYgbQfjbUlmQP-hKJ", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/itAK20q-A994M4PLYJUK9n1HCfEehB6wVcgQpY-thhc", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjNhMTJmNTM4Zjc3ODAzMWM1MDBmMjFlNDgzYTQ2OGRhMTljMzUwMTAifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IlBOakxFWkNTYndlcGx5WFNDa0p0aXciLCJhdWQiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDg0Nzc0MzY4NDc0OTUzODQwNTAiLCJhenAiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU2MTc5OTAsImV4cCI6MTQ1NTYyMTU5MH0.Mr29UuLw1xbUPdNMJQXE6u3lq7W1RP0sMt8dnT5dTBICyw57OiL4PM7MT7Mfrroh-3yKLPly2Sz54OAAewpKUxy_aUxtSki17yfhOe9g9vLTwty6OwkBEja0uUoMwIferyZZBiu7BdHKZEM4rs-mYbk71nc3KdJkw0plC7nnUtfRnzzNN27TuiFGC8aNDX8o_BMLbNVgFcL6s3MJF8_YQWTLXwEk046Kcf658hY_59z6e-5YXEveDPD_QtscEr_MQRomBTHmDWOEVzotyV_axslelEtKWHfSGeTlv_cpb0PJ4sEgCcwmtWZWcRz9GKDE4m5l7bZnD6MIj-n_qFAyvw"}, "client_id": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "071WJgVZK-Rzb7bHyoHn28ao", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/itAK20q-A994M4PLYJUK9n1HCfEehB6wVcgQpY-thhc", "user_agent": null}')

    # joe's creds
    # credentials = OAuth2Credentials.from_json('{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-15T08:24:55Z", "id_token": {"aud": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "IAGbKo5Yf6pplIpDcdghRA", "exp": 1455524695, "azp": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iat": 1455521095, "sub": "110209618710722590711"}, "access_token": "ya29.iQKgr-A57u_U4ULgSMUZpcFQ4oGe1bI74mja4nj4CpLuhbP7AxaNmBVwcHMwHoWq8k9t", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iQKgr-A57u_U4ULgSMUZpcFQ4oGe1bI74mja4nj4CpLuhbP7AxaNmBVwcHMwHoWq8k9t", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/m6mN-o5-tZG9so8vHJAyF6p0W5_msFtXaJwUfulv6bY", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjRjMTgxMzg4MGQ1NjM1Nzg3MTcxMGE0ODlhYWVhY2JkZTU4MGE3N2MifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IklBR2JLbzVZZjZwcGxJcERjZGdoUkEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTAyMDk2MTg3MTA3MjI1OTA3MTEiLCJhenAiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU1MjEwOTUsImV4cCI6MTQ1NTUyNDY5NX0.ipoBdvHVqaET8WWZ51-wRkiMOopjJmMLqNtcuRYtz84rOj2W-qN3LWL52lBISoPyhHYjN0yupFFlYgSrh35yHKEWdCkqJL0-vd-CDSKp8Ca4hC4eah3WUUis9rZ41EIIlrRFuCLmSYgRzv7fvXBReKa-hdEbhkH-9sdOTXOA38i6P8q1dctsJmh93MD6odfG6AGW1FgN4M7ZPaUZnIJLFb2hF0a7rm2AKROUGHRoe3wc8yCnHLTy8jDWL9TgNDC7UReiry2aGkQrXvveIhapVABjcy1lYdZ-k7N1NSzwZcqOxjwvXSj-e1zojsd0q-DoYySjwZ0MYqWTSHu5tqrp-A"}, "client_id": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "071WJgVZK-Rzb7bHyoHn28ao", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/m6mN-o5-tZG9so8vHJAyF6p0W5_msFtXaJwUfulv6bY", "user_agent": null}')
    
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

def build_service():
    credentials = refresh_token()
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('plusDomains', 'v1', http=http)

class GetTicketHandler(webapp2.RequestHandler):
    def get_people(self, circle_id):
        return self.service.people().listByCircle(circleId=circle_id).execute()

    def read_note(self, note_id):
        activities_service = self.service.activities()
        activity = activities_service.get(activityId=note_id).execute()
        return activity.get('object').get('originalContent')

    def get_document(self, document_id):
        activities_service = self.service.activities()
        activity = activities_service.get(activityId=document_id).execute()
        name = activity['title']
        url = activity['object']['attachments'][0]['url']
        return [name, url]

    def get(self):
        t = Ticket.all().filter('assigned', False).get()
        self.service = build_service()
        response = {}
        if t:
            t.assigned = True
            t.put()
            notes = []
            for note_id in t.note_ids:
                notes.append(self.read_note(note_id))
            response = {'id': t.key().id(), 'lat': t.location.lat, 'lon': t.location.lon, 'people': [{'image': person['image']['url'], 'url': person['url']} for person in self.get_people(t.circle_id)['items']] ,'documents': [self.get_document(document_id) for document_id in t.document_ids] , 'location_text': t.location_text, 'location': str(t.location), 'issue_type': t.issue_type, 'equipments': t.equipments, 'services': t.services, 'notes': notes}
        self.response.write(json.dumps(response))

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

class GetPeopleHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(json.dumps(people))

class GetTicketPeopleHandler(webapp2.RequestHandler):
    def get(self):
        tag = self.request.get('tag')
        self.response.write(json.dumps(tags_to_people[tag]))

class GetTagsHandler(webapp2.RequestHandler):
    def get(self):
        ret_val = [[t.title(), t] for t in tags]
        self.response.write(json.dumps(ret_val))

class TempHandler(webapp2.RequestHandler):
    def create_circle(self, ticket_id):
        new_circle = {
            'displayName': str(ticket_id)
        }
        resp = self.service.circles().insert(userId = 'me', body = new_circle).execute()
        return resp['id']

    def create_ticket(self, assigned=False):
        lat = self.request.get('lat')
        lng = self.request.get('lng')
        issue_type = self.request.get('issue-type')
        equipments = self.request.get('equipments').split('#$#')
        services = self.request.get('services').split('#$#')
        location = GeoPt(lat, lng)
        location_text = self.request.get('location_text')
        # documents = self.request.get('documents').split('#$#')
        ticket = Ticket(location=location, location_text=location_text, assigned=assigned, issue_type=issue_type, equipments=equipments, services=services)
        ticket.put()
        return ticket.key().id()

    def add_to_circle(self, user_id, circle_id):
        add_service = self.service.circles().addPeople(circleId=circle_id, userId=user_id)
        add_service.execute()

    def create_note(self, note, circle_id):
        body = {"object": {"originalContent": note, "objectType": "note"}, "access": { "items": [{"dispalyName": "circle", "type": "circle", "id": str(circle_id)}] , "domainRestricted": True}}
        activity_service = self.service.activities().insert(userId='me', body=body)
        return activity_service.execute()['id']

    def update_ticket(self, ticket_id, circle_id, note_ids, document_ids):
        ticket = Ticket.get_by_id(ticket_id)
        ticket.circle_id = circle_id
        ticket.note_ids = note_ids
        ticket.document_ids = document_ids
        ticket.put()

    def create_documents(self, name, url, circle_id):
        body = {"object": {"originalContent": name, "attachments": [{"objectType": "article", "url": url}]}, "access": { "items": [{"dispalyName": "circle", "type": "circle", "id": str(circle_id)}] , "domainRestricted": True}}
        activity_service = self.service.activities().insert(userId='me', body=body)
        return activity_service.execute()['id']

    def post(self):
        self.service = build_service()
        notes = self.request.get('notes').split('#$#')
        note_ids = []
        ticket_id = self.create_ticket()
        circle_id = self.create_circle(ticket_id)
        document_ids = [self.create_documents(d.split(' :: ')[0], d.split(' :: ')[1], circle_id) for d in self.request.get('documents').split('#$#')]
        for note in notes:
            note_ids.append(self.create_note(note, circle_id))
        self.update_ticket(ticket_id, circle_id, note_ids, document_ids)
        engineer = self.request.get('engineer')
        self.add_to_circle(engineer, circle_id)
        people = tags_to_people[self.request.get('issue-type')]
        if 'engineers' in people:
            for eng in people['engineers']:
                self.add_to_circle(eng[1], circle_id)
        if 'experts' in people:
            for eng in people['experts']:
                self.add_to_circle(eng[1], circle_id)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({'ticket_id':ticket_id}))

    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'collision.html')
        self.response.out.write(template.render(path, {}))

app = webapp2.WSGIApplication([
                                ('/', MainPage),
                                ('/auth', AuthHandler),
                                ('/tickets/get', GetTicketHandler),
                                ('/circles/get', GetCirclesHandler),
                                ('/circles/assign', AssignCirclesHandler),
                                ('/notes/create', CreateNoteHandler),
                                ('/notes/get', GetNotesHandler),
                                ('/people/get', GetPeopleHandler),
                                ('/tickets/get_people', GetTicketPeopleHandler),
                                ('/tags/get', GetTagsHandler),
                                ('/tickets/create', TempHandler),
                            ], debug=True)