import json
import httplib2

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials

def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/plus.me',
              'https://www.googleapis.com/auth/plus.stream.write',
              'https://www.googleapis.com/auth/plus.stream.read',
              'https://www.googleapis.com/auth/plus.circles.write',
              'https://www.googleapis.com/auth/plus.circles.read']

    REDIRECT_URI = 'http://oscarosl-test.appspot.com'

    CLIENT_ID = '255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com'
    CLIENT_SECRET = '071WJgVZK-Rzb7bHyoHn28ao'

    flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                               client_secret=CLIENT_SECRET,
                               scope=SCOPES,
                               redirect_uri=REDIRECT_URI,
                               approval_prompt='force')

    auth_uri = flow.step1_get_authorize_url()

    print 'Please paste this URL in your browser to authenticate this program.'
    print auth_uri
    code = raw_input('Enter the code it gives you here: ')

    credentials = flow.step2_exchange(code)
    return credentials

credentials = get_credentials()
print credentials.to_json()

'''
# credentials_json = '{"_module": "oauth2client.client", "token_expiry": "2016-02-05T09:03:10Z", "access_token": "ya29.fwLqgPt8KrQgGLba8clW300f-7KCcSPeuBR8uH5BIGR4-74P2mn0XWnr6WtS7zxV744b", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.fwLqgPt8KrQgGLba8clW300f-7KCcSPeuBR8uH5BIGR4-74P2mn0XWnr6WtS7zxV744b", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/y4jDrWImRezvaB6uCmh8ziHZraEf_JM5atkVYNgdA5k", "id_token": {"aud": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "Mi1H-Y8jMn6wlSXWgrl4GA", "exp": 1454662990, "azp": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iat": 1454659390, "sub": "106258495568677784165"}}, "client_id": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "id_token": {"aud": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "Mi1H-Y8jMn6wlSXWgrl4GA", "exp": 1454662990, "azp": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iat": 1454659390, "sub": "106258495568677784165"}, "client_secret": "071WJgVZK-Rzb7bHyoHn28ao", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/y4jDrWImRezvaB6uCmh8ziHZraEf_JM5atkVYNgdA5k", "user_agent": null}'
# credentials = OAuth2Credentials.from_json(credentials_json)

http = httplib2.Http()
http = credentials.authorize(http)
service = build('plusDomains', 'v1', http=http)


def create_circle(name, description):
    new_circle = {
        'displayName': name,
        'description': description
    }
    return service.circles().insert(userId = 'me', body = new_circle).execute()

def get_circles(user_id='me'):
    circle_service = service.circles()
    request = circle_service.list(userId=user_id)

    circle_list = request.execute()
    return circle_list

def get_circle(circle_id):
    circle_service = service.circles()
    return circle_service.get(circleId=circle_id).execute()

def add_people(user_id, circle_id):
    add_service = service.circles().addPeople(circleId=circle_id, userId=user_id)
    return add_service.execute()  

def create_note(content, user_id='me'):
    body = {"object": {"originalContent": content, "objectType": "note"}, "access": {"domainRestricted": True}}
    activity_service = service.activities().insert(userId=user_id, body=body)
    return activity_service.execute()

def get_activities(user_id='me'):
    activity_service = service.activities().list(userId=user_id, collection="user")
    return activity_service.execute()

def get_activity(activity_id):
    activity_service = service.activities().get(activityId=activity_id)
    return activity_service.execute()

# print get_activities()
# print create_note()
# create_circle('another circle', 'another circles desc')
# print get_circles()
# print add_people('100163556704457768400' ,'7b5344760a7aee3d')
# https://www.googleapis.com/plusDomains/v1/people/me/circles?access_token=ya29.fgKqDkSOb3a--9TjFH9u6EhR8f2xR-k3i65h1McpKY5Q713f0eaaeP96OQ7omYwqQNzH
'''