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

from models.ticket import Ticket, LastAssignedTicket
from google.appengine.ext.db import GeoPt

job_id_map = {
	'#1234':{'location':{'addr':'133 W 44th St, New York, NY 10036, USA', 'lat':'40.756903', 'lon':'-73.984376'},'issue':{'type':'repair/maintenance'}, 'equipments':['Widget Box 2', 'Analyzer A', 'Monitor Plus 1.0', 'Toolkit Z'], 'services':['Mid Sized Business Plus Package'], 'engineer':{'id':'110257721827374623737', 'name':'Joe'}, 'customer':{'id':'103764585826277201640', 'name':'Rick'}, 'notes':['Repair and maintenance of several items'], 'documents':['Doc1 :: URL1']},
	'#2345':{'location':{'addr':'823 11th Ave, New York, NY 10019, USA', 'lat':'40.770048', 'lon':'-73.992164'},'issue':{'type':'installation'}, 'equipments':['Machine 2', 'Analyzer A', 'Monitor Plus 1.0', 'Apparatus v2'], 'services':['Small Business Basics'], 'engineer':{'id':'110257721827374623737', 'name':'Joe'}, 'customer':{'id':'108560908635605545932', 'name':'Robert'}, 'notes':['Installation of several items'], 'documents':['Doc2 :: URL2']},
	'#3456':{'location':{'addr':'445 W 59th St, New York, NY 10019, USA', 'lat':'40.770288', 'lon':'-73.986705'},'issue':{'type':'repair/maintenance'}, 'equipments':['Machine 1', 'Toolkit A3'], 'services':['Home Essentials Package'], 'engineer':{'id':'110257721827374623737', 'name':'Joe'}, 'customer':{'id':'102345940077083980832', 'name':'Ryan'}, 'notes':['Repair and maintenance of several items'], 'documents':['Doc3 :: URL3']},
	'#4567':{'location':{'addr':'665 5th Ave, New York, NY 10022, USA', 'lat':'40.760084', 'lon':'-73.975604'},'issue':{'type':'repair/maintenance'}, 'equipments':['Appliance 1', 'Toolkit X', "10' Cables"], 'services':['Enterprise Economy Bundle'], 'engineer':{'id':'110257721827374623737', 'name':'Joe'}, 'customer':{'id':'107612119418245526899', 'name':'Rachel'}, 'notes':['Repair and maintenance of several items'], 'documents':['Doc4 :: URL4']},
	'#5678':{'location':{'addr':'524 Park Ave, New York, NY 10065, USA', 'lat':'40.763868', 'lon':'-73.969638'},'issue':{'type':'estimate/inspection'}, 'equipments':['Appliance Model 2', 'Tracker Module', 'Receipt Pad'], 'services':['Diamond Enterprise Bundle'], 'engineer':{'id':'110257721827374623737', 'name':'Joe'}, 'customer':{'id':'108612246962932756480', 'name':'Rose'}, 'notes':['Estimation and inspection of several items'], 'documents':['Doc5 :: URL5']}
}

engineer_creds = {
    'joe': '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-17T09:23:30Z", "id_token": {"aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "__kE3kZ9FZTnH77RoEG2vw", "exp": 1455701010, "azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455697410, "sub": "110257721827374623737"}, "access_token": "ya29.iwJDdTtHKFLrRE-Jz37z4-8I1uyiV2Gm0OGqxUj_6fGVAgZOD2djhJ8mnLosDmgA7CS7", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iwJDdTtHKFLrRE-Jz37z4-8I1uyiV2Gm0OGqxUj_6fGVAgZOD2djhJ8mnLosDmgA7CS7", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/xC2iWOZC2_YgNEegWU0PuiE3CG1fYdMNocR9KO3sQuo", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImRhNTIyODMyNzY0N2YwOGE1NDdkMjczZmFjNmIxMmM5NjliMzllZWIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6Il9fa0Uza1o5RlpUbkg3N1JvRUcydnciLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTAyNTc3MjE4MjczNzQ2MjM3MzciLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU2OTc0MTAsImV4cCI6MTQ1NTcwMTAxMH0.ffj76PYsNLaZ4v4cIlKtvk8f-_Zx3TLoeORlHGP1YtAq2ninAbepfA69KvO7oVJZprnnwUBaj2Hm7Vuf2h-4E9tMXy-97EljcIlAVwBgk9aYm9HHx-JOX3YsEVp-iiqOGVxEIMI71rLTjmNFJHRXjSd9JR_Pzb__XkqRdeqrThnXA-9i9WW9hNWsPm4ITlz5L2BJfBscjT9tRXAvij6_-5zImjborCbb2OxS0mRcEVkL3gHCYkDH6HUlOIVoyx-9ZCHUgu1XZUR9CF6vrDeGaOExe7SMxzQrAV_ctJpU-NfDhGMLS6syAbe1OkUcdgl8VZ9ekUTMloble_gaXZ71Sg"}, "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/xC2iWOZC2_YgNEegWU0PuiE3CG1fYdMNocR9KO3sQuo", "user_agent": null}',
    'josephine': '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-17T09:24:47Z", "id_token": {"aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "Mh0gDgd9p7UMNMbXWQTM8A", "exp": 1455701087, "azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455697487, "sub": "117685299168782698970"}, "access_token": "ya29.iwLJejtI549P7dr1xWuSPD4Lm2Y5neVyk5I6HoBUwFjEHWuL0-EGzexG0xRiRUopBd73", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iwLJejtI549P7dr1xWuSPD4Lm2Y5neVyk5I6HoBUwFjEHWuL0-EGzexG0xRiRUopBd73", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/n2Ssv-NKY6Sk_yFRx4ufmpy9ghzytEXOvacBvLvghlk", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImRhNTIyODMyNzY0N2YwOGE1NDdkMjczZmFjNmIxMmM5NjliMzllZWIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6Ik1oMGdEZ2Q5cDdVTU5NYlhXUVRNOEEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTc2ODUyOTkxNjg3ODI2OTg5NzAiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU2OTc0ODcsImV4cCI6MTQ1NTcwMTA4N30.Ts_Btq-9u4VCNdA5SH7ZywcVcZKHTkODiW0lyaJ5K91ckSYIUeq1FOynp9fVyCtGImXrlaisdvjjUGIjUU21ghnYzIcDmKrd9wCgLJvrL7jeSeWiocyJymKsshx-Jd94JbxmBqyOzVZywQvpxwgh6ZwtMfy3RHBgZ0G2BWVWVwBnz8FQ5i1gDp4y3zfbE1bo9Yw_WGKwpSi8rxE7M7CSx-MIKU1yWOhITYhTdfXH7RemCzsn_GCxSk_slPJBeGhGKlmgZmnqUvPAQtbCCREvDwuCKHStJfQ6949LeVZKNWPoNojACDos4giHNoKse320BXC_CcKAHYAx2WpGdsgrhA"}, "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/n2Ssv-NKY6Sk_yFRx4ufmpy9ghzytEXOvacBvLvghlk", "user_agent": null}',
    'jeremy': '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-17T09:25:29Z", "id_token": {"aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "tzfHxMCWGwcZmSC5zCIBEA", "exp": 1455701129, "azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455697529, "sub": "101967792556257735208"}, "access_token": "ya29.iwLDmYYLWNSZDONoLT7bxHhe3V5UjU0xB9t6RhtNxKuGHshoXuVgpoYCYMb1EwP3_bwa", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iwLDmYYLWNSZDONoLT7bxHhe3V5UjU0xB9t6RhtNxKuGHshoXuVgpoYCYMb1EwP3_bwa", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/GqBZEVlQd2TixLKO7onmQSYIU592Z2Ec9QGa8cjGhmQ", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImRhNTIyODMyNzY0N2YwOGE1NDdkMjczZmFjNmIxMmM5NjliMzllZWIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6InR6Zkh4TUNXR3djWm1TQzV6Q0lCRUEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDE5Njc3OTI1NTYyNTc3MzUyMDgiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU2OTc1MjksImV4cCI6MTQ1NTcwMTEyOX0.C3w8nKVuETT97Nk50YNw-XAMOYxykU9GR3U4T4ZIy3xnNf_4PEGCuheo44v-5UZoGIMsveLWFEvfxeHmLO27kxCvtreEMHHKylgLzrqVx7aLf-N88a1Lz8Uy3dcmZOWtXzSFmIa0BMoyM1BKFCCogoGzPv4Px63ICMiwB3kf8MyVGZvvOOgU3cPvMJBTPKVJZR6LltwVWnrWkBkSUxbpVJowE-zjFH_NaiSZBh_-BCS-4EJGuuRuW2NPamDzKpMMitJjbY5xAqI-sigfAyYhRxOGDMMHo1qdhw-I51Y6AZ5_c6sZrxWT_SLG9sQWdG3Zb0MPCZCLqM6toIeNOq9LZg"}, "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/GqBZEVlQd2TixLKO7onmQSYIU592Z2Ec9QGa8cjGhmQ", "user_agent": null}',
    'jhon': '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-17T09:26:10Z", "id_token": {"aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "6JOkop9WU_UHQmHBqRF3lA", "exp": 1455701170, "azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455697570, "sub": "103387629180365578874"}, "access_token": "ya29.iwLtc6PmfkNGBmnuTiNxAE7aXzL7ZOaaR5xeGqOBwF_-Wv9A_xr-hModfKvNpzY4F1aP", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iwLtc6PmfkNGBmnuTiNxAE7aXzL7ZOaaR5xeGqOBwF_-Wv9A_xr-hModfKvNpzY4F1aP", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/jorNHDWENkFfSN-cZZGlszs8RxvXO_NQzBg5vCk3I5g", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImRhNTIyODMyNzY0N2YwOGE1NDdkMjczZmFjNmIxMmM5NjliMzllZWIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IjZKT2tvcDlXVV9VSFFtSEJxUkYzbEEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDMzODc2MjkxODAzNjU1Nzg4NzQiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU2OTc1NzAsImV4cCI6MTQ1NTcwMTE3MH0.Qs_8Gg_onxqiji_RwBV9Mtd2mfKdm_fOQ0jX1w6bWPGhxT1cCgkZ9_9b70K5QiCw8NGksLI_CfOiK2Pm5j1mdalgefSSwqhoXCDYpnArEl5n_Zt6ijxd4oaxTxJMsLNrm-ghPX4BfmZsvf16V-hlhlxKZbQklbhGEVJpshkDXwt9QwhnPCgp3A298viHhSHKqnbQAzgyQF-LtkLcNsRfAbkaQiZhnqB2bFWcZXj7A9TqWdJawUnBhHbaZjzxePi0m4JXyAV3ef9_yZvJXOScwMZiZ4ugmMhXb8rPjFQygCOcq6VRHG7bVplKhwgzkNNNAaUSor4vEg0zQYzKdhWWjg"}, "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/jorNHDWENkFfSN-cZZGlszs8RxvXO_NQzBg5vCk3I5g", "user_agent": null}',
    'james': '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-17T09:27:29Z", "id_token": {"aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "jCzT1sZrnd_F0AQuex5PvA", "exp": 1455701249, "azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455697649, "sub": "101447084593147265288"}, "access_token": "ya29.iwLunWr77FuylIzGEx5eYknoEGPyWM518T9uMxxT4hsVibXpXGMMBU9Ij3pTyl090kp6", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iwLunWr77FuylIzGEx5eYknoEGPyWM518T9uMxxT4hsVibXpXGMMBU9Ij3pTyl090kp6", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/-rF9zE6C4TVIS4JNTEy_M42PAwBT6HsYOe-cGHNn2zdIgOrJDtdun6zK6XiATCKT", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImRhNTIyODMyNzY0N2YwOGE1NDdkMjczZmFjNmIxMmM5NjliMzllZWIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6ImpDelQxc1pybmRfRjBBUXVleDVQdkEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDE0NDcwODQ1OTMxNDcyNjUyODgiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU2OTc2NDksImV4cCI6MTQ1NTcwMTI0OX0.I09pm9iz99q1SNcN1zQbbzgqx5oKbC92Ubxb3RkvAsQ9Xqw4ppodXFTeM7p18BF6BZare21ZF43l-oujjOx_REGsOVtBtX9qg5qrUtCPGEOgD6oS3dRlg5NHLychVc7FvbdcfFrY6rxvq9k_-jJMb2W7kWjuYkTBII0U1zrCQSMS8THMhVjz9GRHBCkZbnamUX38LgfliFEzmxSwmx4sNx2OzK_T1jnFTt0TAetJSQqvxZhNLv-554YkZwEgZSzqr8YgDDVMp3mY6q13mB2ipbk6nlTDZNbnFo9leppr85zEypWq-bjxD0qRJ6W_hl9mn4PUVns6QO1UBPlLxtTVwg"}, "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/-rF9zE6C4TVIS4JNTEy_M42PAwBT6HsYOe-cGHNn2zdIgOrJDtdun6zK6XiATCKT", "user_agent": null}',
    'jenny': '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-17T09:28:03Z", "id_token": {"aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "igDtWM0ey4YAvdr6ZBCPNg", "exp": 1455701282, "azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455697682, "sub": "102417683683083682579"}, "access_token": "ya29.iwK4CmD8fhd7PHCFVbhATwJgvpAlHPOnuWwhebmhXh8gMoN__PZUT_BQt0UR4hwmKMSW", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iwK4CmD8fhd7PHCFVbhATwJgvpAlHPOnuWwhebmhXh8gMoN__PZUT_BQt0UR4hwmKMSW", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/_2iGSrTZ-R_cDydjYJj632acRsmttsgaEXMUeVkw0Pc", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImRhNTIyODMyNzY0N2YwOGE1NDdkMjczZmFjNmIxMmM5NjliMzllZWIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6ImlnRHRXTTBleTRZQXZkcjZaQkNQTmciLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDI0MTc2ODM2ODMwODM2ODI1NzkiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU2OTc2ODIsImV4cCI6MTQ1NTcwMTI4Mn0.hPJFRH7Bo4WPe1-9Nr3dkKxZobrCLVk_PSCk2T9EOjglGPvgbTDS9icUiU-47GUTkpKtuK00CXSpcbCfBrIX7xA4Bpv6i70vbdUt-R8IW5fZmiYI9_rdTrAUipy0dfJ2eNIyZHig3jNKl9eNAqfEQjbinJ9PPo6uwqxRRImfuVYuA0tFulf7cNV4gLqOZC5Rhvqv64yKeTMZKX-xRyxjNXTWe8dtrycTzSuvFtjiRZZQPAdTviNPVLm_AERZfDUu_bvhivxZLOW5kb3oEGLhsgOoEkTT8C6MCjRSA6UCjb026ui6fL0ivalvuS_AUjeMnxl-ciNmNu-W6Uq-mNediQ"}, "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/_2iGSrTZ-R_cDydjYJj632acRsmttsgaEXMUeVkw0Pc", "user_agent": null}',
    'jeff': '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-17T09:28:25Z", "id_token": {"aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "EUvkzZSQhfCfSpnBem_WAw", "exp": 1455701305, "azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455697705, "sub": "115781491509522514753"}, "access_token": "ya29.iwK5epeEWqHxxHy5jmngGFfv2oSicW9LPa-15eame0tJhzTEVfjqwwOnDuWA3vFqE14y", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iwK5epeEWqHxxHy5jmngGFfv2oSicW9LPa-15eame0tJhzTEVfjqwwOnDuWA3vFqE14y", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/Mc541-S8qchh1Mv1nBnwSoRTMLN4-i61kWnptLG8eFdIgOrJDtdun6zK6XiATCKT", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImRhNTIyODMyNzY0N2YwOGE1NDdkMjczZmFjNmIxMmM5NjliMzllZWIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IkVVdmt6WlNRaGZDZlNwbkJlbV9XQXciLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTU3ODE0OTE1MDk1MjI1MTQ3NTMiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU2OTc3MDUsImV4cCI6MTQ1NTcwMTMwNX0.c5gFIIFtKegVo1tk96yS_OMyCXkcU2ALYRt4Y_ppucdjzY2qKCh4bZ4fj3YErE6KFzy9Pq_vULD02uXxfB3O--ARgumAeDGRSeD41nB5x7zPjNWWqH4gYZzSSzI27-PrmCrpz9lsxUrr1ft4QAxm5HfMT5Zh8tJi2iUOsAUTuAJjbvSS7epCMWm1QRdeORLg4iwUPJBkYVB0DPSkASafpUPlmc42LPO890cngOpevkqIBGM4RF57LVMUEUQiz_KEg6G2EBQuAQJkVHRyGBUnnPLUYvs8FtO_u4GM6dMsBWrVdGI-b8RpS11AfgQ6IWELg0_WuEvQzW3uP1S6xHm2Lw"}, "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/Mc541-S8qchh1Mv1nBnwSoRTMLN4-i61kWnptLG8eFdIgOrJDtdun6zK6XiATCKT", "user_agent": null}',
    'jason': '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-17T09:28:46Z", "id_token": {"aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "7hnB5ydWwwzuMWii9HQdIw", "exp": 1455701326, "azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455697726, "sub": "105193078925726528104"}, "access_token": "ya29.iwJTfIjNdTsh4ZesIQIzveZYny2aaFlWfVKBUTXIXK-ZrvIfGGvicZwT3XpPImyLQEj9", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iwJTfIjNdTsh4ZesIQIzveZYny2aaFlWfVKBUTXIXK-ZrvIfGGvicZwT3XpPImyLQEj9", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/qTo2escEPW0OOe_E_jkX9Zh3VYZvejpfohKhBLFC0mk", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImRhNTIyODMyNzY0N2YwOGE1NDdkMjczZmFjNmIxMmM5NjliMzllZWIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IjdobkI1eWRXd3d6dU1XaWk5SFFkSXciLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDUxOTMwNzg5MjU3MjY1MjgxMDQiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU2OTc3MjYsImV4cCI6MTQ1NTcwMTMyNn0.INiiTDV3QPoLua0l5ena5kZo0buHAW-1qMbfUSAHxvaTay3BrRXCTYCu2NC6LwAINK0Bbf7U1vvRG1cyxgYWchkBrgKLNjvSnYPXNyQqvgQMtSYdP9nNQTZ-oZ9IE82s0djCObs-k1xDDx678EiqZmfIeVk3shqq0MbCFggXzefbCovheYaw8Er_EWFmMBoKytnM71El-IztfnZeq1lNR2GHMw9uuxIUPmZ9pqMsKOXFhPIssd1JUZ2Ya9-_knaoRtoFUmnwPZ3YbsUP1ra5NPytKOtI9Fh7GNG2di_YfE5x-gQoqEK7QeByL_6UVne3dC8_EaKZ4VBqoMQ80q3ubw"}, "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/qTo2escEPW0OOe_E_jkX9Zh3VYZvejpfohKhBLFC0mk", "user_agent": null}',
    'jenna': '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-17T09:29:06Z", "id_token": {"aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "3eX-YF3EPOyWTPuJNNBEag", "exp": 1455701346, "azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455697746, "sub": "109061817072269062716"}, "access_token": "ya29.iwLxNG51OfMLJjlnzWcAPaWBl1qHiSAW0iA2GzCRvCQ1YljlUriECYaUHnk6LPO0p163", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iwLxNG51OfMLJjlnzWcAPaWBl1qHiSAW0iA2GzCRvCQ1YljlUriECYaUHnk6LPO0p163", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/paFFVqGimY1ey9Zqy-h9BGqohSqBFNijm3jZ9LekA8A", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImRhNTIyODMyNzY0N2YwOGE1NDdkMjczZmFjNmIxMmM5NjliMzllZWIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IjNlWC1ZRjNFUE95V1RQdUpOTkJFYWciLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDkwNjE4MTcwNzIyNjkwNjI3MTYiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU2OTc3NDYsImV4cCI6MTQ1NTcwMTM0Nn0.JYL52XXU3WsiPQwA8piKlT99KDmN9fcfshqydsK7_bnD4Eep0-g2_1oJ5jwlLmT9kUHVySgia02Xws7d2_Mb0MCaK5A82wam0DLWrkAiOlS2hK9ETvRBBh6XKNLZK9HeCnKs9l6AGB08iLmGzfqNwhtYa_ohBXPbn90f1hhKMLx0EXBjZwpy1lGHxIvR0RpKZoW9Ta3053LiXm7V72ahtwPMB7XklaZbrZwEn0v50fUsukDyqSrREQJ8QKTl4FjXraydPMHdww1YwXwYGnQtaX9jOPWp6JtoL1COgiRjhkjkJKGpXRxfrxSMo9oQMdMqvCjJAg04qsQaCJUF1hiduQ"}, "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/paFFVqGimY1ey9Zqy-h9BGqohSqBFNijm3jZ9LekA8A", "user_agent": null}'
}

people = {'customers':[['Rick','103764585826277201640'], ['Robert','108560908635605545932'], ['Ryan','102345940077083980832'],['Rachel','107612119418245526899'],['Rose','108612246962932756480']],
          'engineers':[['Joe','110257721827374623737'],['Josephine','117685299168782698970'],['Jeremy','101967792556257735208'],['Jhon','103387629180365578874'],['James','101447084593147265288'],['Jenny','102417683683083682579'],['Jeff','115781491509522514753'],['Jason','105193078925726528104'],['Jenna','109061817072269062716']],
          'experts':[['TWC','112739138406530779564'],['Cisco','110132770680215220078'],['Verizon','108741317245837764468'],['Belkin','112043759976089842597'],['Apple','103675625919779944270'],['Netgear','118014758899268715696']]}

tags = ['installation' , 'repair/maintenance', 'replacement', 'delivery', 'meter reading', 'estimate/inspection']

tags_to_people = {'installation': {'experts': [['TWC', '112739138406530779564']], 'engineers': [['Jhon', '103387629180365578874'], ['Jeff', '115781491509522514753'], ['Jenna', '109061817072269062716']]}, 'meter reading': {'experts': [['Apple', '103675625919779944270']]}, 'delivery': {'experts': [['Cisco', '110132770680215220078']], 'engineers': [['Jason', '105193078925726528104']]}, 'repair/maintenance': {'experts': [['Netgear', '118014758899268715696']], 'engineers': [['Josephine', '117685299168782698970']]}, 'estimate/inspection': {'engineers': [['Jenny', '102417683683083682579'], ['Joe', '110257721827374623737'], ['James', '101447084593147265288']]}, 'replacement': {'experts': [['Belkin', '112043759976089842597'], ['Verizon', '108741317245837764468']], 'engineers': [['Jeremy', '101967792556257735208']]}}

id_to_name = {'103387629180365578874': 'Jhon', '118014758899268715696': 'Netgear', '101967792556257735208': 'Jeremy', '110132770680215220078': 'Cisco', '117685299168782698970': 'Josephine', '112739138406530779564': 'TWC', '115781491509522514753': 'Jeff', '102417683683083682579': 'Jenny', '110257721827374623737': 'Joe', '112043759976089842597': 'Belkin', '103675625919779944270': 'Apple', '109061817072269062716': 'Jenna', '108741317245837764468': 'Verizon', '101447084593147265288': 'James', '105193078925726528104': 'Jason'}

def refresh_token(engineer):
    # peggy's creds
    # credentials = OAuth2Credentials.from_json('{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-16T11:19:50Z", "id_token": {"aud": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "PNjLEZCSbweplyXSCkJtiw", "exp": 1455621590, "azp": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iat": 1455617990, "sub": "108477436847495384050"}, "access_token": "ya29.igLy8L3IGaYFaht5K8sxDWBhcw_zyajnkNvcrWeOgAarX7GI97zZYgbQfjbUlmQP-hKJ", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.igLy8L3IGaYFaht5K8sxDWBhcw_zyajnkNvcrWeOgAarX7GI97zZYgbQfjbUlmQP-hKJ", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/itAK20q-A994M4PLYJUK9n1HCfEehB6wVcgQpY-thhc", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjNhMTJmNTM4Zjc3ODAzMWM1MDBmMjFlNDgzYTQ2OGRhMTljMzUwMTAifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IlBOakxFWkNTYndlcGx5WFNDa0p0aXciLCJhdWQiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDg0Nzc0MzY4NDc0OTUzODQwNTAiLCJhenAiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU2MTc5OTAsImV4cCI6MTQ1NTYyMTU5MH0.Mr29UuLw1xbUPdNMJQXE6u3lq7W1RP0sMt8dnT5dTBICyw57OiL4PM7MT7Mfrroh-3yKLPly2Sz54OAAewpKUxy_aUxtSki17yfhOe9g9vLTwty6OwkBEja0uUoMwIferyZZBiu7BdHKZEM4rs-mYbk71nc3KdJkw0plC7nnUtfRnzzNN27TuiFGC8aNDX8o_BMLbNVgFcL6s3MJF8_YQWTLXwEk046Kcf658hY_59z6e-5YXEveDPD_QtscEr_MQRomBTHmDWOEVzotyV_axslelEtKWHfSGeTlv_cpb0PJ4sEgCcwmtWZWcRz9GKDE4m5l7bZnD6MIj-n_qFAyvw"}, "client_id": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "071WJgVZK-Rzb7bHyoHn28ao", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/itAK20q-A994M4PLYJUK9n1HCfEehB6wVcgQpY-thhc", "user_agent": null}')

    # joe's creds
    # credentials = OAuth2Credentials.from_json('{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-15T08:24:55Z", "id_token": {"aud": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "IAGbKo5Yf6pplIpDcdghRA", "exp": 1455524695, "azp": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iat": 1455521095, "sub": "110209618710722590711"}, "access_token": "ya29.iQKgr-A57u_U4ULgSMUZpcFQ4oGe1bI74mja4nj4CpLuhbP7AxaNmBVwcHMwHoWq8k9t", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iQKgr-A57u_U4ULgSMUZpcFQ4oGe1bI74mja4nj4CpLuhbP7AxaNmBVwcHMwHoWq8k9t", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/m6mN-o5-tZG9so8vHJAyF6p0W5_msFtXaJwUfulv6bY", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjRjMTgxMzg4MGQ1NjM1Nzg3MTcxMGE0ODlhYWVhY2JkZTU4MGE3N2MifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IklBR2JLbzVZZjZwcGxJcERjZGdoUkEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTAyMDk2MTg3MTA3MjI1OTA3MTEiLCJhenAiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU1MjEwOTUsImV4cCI6MTQ1NTUyNDY5NX0.ipoBdvHVqaET8WWZ51-wRkiMOopjJmMLqNtcuRYtz84rOj2W-qN3LWL52lBISoPyhHYjN0yupFFlYgSrh35yHKEWdCkqJL0-vd-CDSKp8Ca4hC4eah3WUUis9rZ41EIIlrRFuCLmSYgRzv7fvXBReKa-hdEbhkH-9sdOTXOA38i6P8q1dctsJmh93MD6odfG6AGW1FgN4M7ZPaUZnIJLFb2hF0a7rm2AKROUGHRoe3wc8yCnHLTy8jDWL9TgNDC7UReiry2aGkQrXvveIhapVABjcy1lYdZ-k7N1NSzwZcqOxjwvXSj-e1zojsd0q-DoYySjwZ0MYqWTSHu5tqrp-A"}, "client_id": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "071WJgVZK-Rzb7bHyoHn28ao", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/m6mN-o5-tZG9so8vHJAyF6p0W5_msFtXaJwUfulv6bY", "user_agent": null}')
    
    # ranju's creds
    # credentials = OAuth2Credentials.from_json('{"user_agent": null, "access_token": "ya29.hgLC-ipSDIJ5kpEntB5LBpHhItUoeF2uChvRIKrY371fyVvgIpnIRIl-I2NPGpfNDLqs", "token_expiry": "2016-02-12T12:35:37Z", "scopes": ["https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.read", "https://www.googleapis.com/auth/plus.me"], "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "invalid": false, "client_secret": "1kk1vYbu8hKBz_GxYjJl6Frm", "refresh_token": "1/Ecq-WjOjv8MHaHTGttxWTrAGXxaIJk044PuNSKF75MxIgOrJDtdun6zK6XiATCKT", "token_uri": "https://accounts.google.com/o/oauth2/token", "client_id": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "token_response": {"token_type": "Bearer", "refresh_token": "1/Ecq-WjOjv8MHaHTGttxWTrAGXxaIJk044PuNSKF75MxIgOrJDtdun6zK6XiATCKT", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImE0MTYzNjE5NDIzZGNkM2E3MzYxYWNmMmE2NDFiZjZmN2M5ZTQ4OGEifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6ImZqd1RhbF9tN1J5bVVqazY1TnlZUVEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTA5MzI2ODYyNjQyMzgwNzMxMDQiLCJhenAiOiIyNTU1NTUxMTA4MDYtNWQ4NWw4OWs1YzZvZmRpaHA2ZmNmbGl0ODZmb2F0ZmMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTUyNzY5MzYsImV4cCI6MTQ1NTI4MDUzNn0.CIp7kSf5G_TsDaSzZBWTB8jRZOLZizJq4YGbXM_KYeA1JFf3iWFN53Ifk6hUNw1X6A6nl_BVoe4lqWK9eXneGmTIABTpNSWHam9ZXW8b6JpAJVvoUjlQNBKwbVI5dXSd6UdWZCJ6VS8btVI9NjzTNTCvroa3LeNycYPfugZ-NmdTfcm7cEJ7LPN2hfcuDhWU_sZ5xNNzzcEEz3w_7zAQTfIoX1Ufi81o1PzLvlHp5hxyEle-kepbC6XTd4ZekbJBO6DafGQCU6fwNuNRnJFr0HuEbxMrcqMvVCa6yVjezIta0NvKFC2SjADTR6yTCYUFH1hIspC2NYh6_5hWGJdBjQ", "access_token": "ya29.hgLC-ipSDIJ5kpEntB5LBpHhItUoeF2uChvRIKrY371fyVvgIpnIRIl-I2NPGpfNDLqs", "expires_in": 3600}, "id_token": {"azp": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "aud": "255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com", "iat": 1455276936, "exp": 1455280536, "sub": "110932686264238073104", "at_hash": "fjwTal_m7RymUjk65NyYQQ", "iss": "accounts.google.com"}, "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "_module": "oauth2client.client"}')
    
    # vvvv ashray's creds, don't upoad to appengine vvvv
    # credentials = OAuth2Credentials.from_json('{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/plus.circles.read", "https://www.googleapis.com/auth/plus.circles.write", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.read"], "token_expiry": "2016-02-15T07:07:40Z", "id_token": {"aud": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iss": "accounts.google.com", "at_hash": "CQblAMCAH9O0ZNYAxG1zZA", "exp": 1455520059, "azp": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "iat": 1455516459, "sub": "106258495568677784165"}, "access_token": "ya29.iQKHPJJyuIkGIfVAf1qwNEDwINXElO_H5XtWEBq_GBKLB87PmcH_qF1EhQgIhEBZRBZ2", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.iQKHPJJyuIkGIfVAf1qwNEDwINXElO_H5XtWEBq_GBKLB87PmcH_qF1EhQgIhEBZRBZ2", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/fxyAKw-rmpmHD9AEsJrC-9NP7Tt_aHI4-M028GwYvNBIgOrJDtdun6zK6XiATCKT", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjRjMTgxMzg4MGQ1NjM1Nzg3MTcxMGE0ODlhYWVhY2JkZTU4MGE3N2MifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IkNRYmxBTUNBSDlPMFpOWUF4RzF6WkEiLCJhdWQiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDYyNTg0OTU1Njg2Nzc3ODQxNjUiLCJhenAiOiIyNTU1NTUxMTA4MDYtNGxrMm1vdTNvZWswaGs3bDlycG5lZ2FxYWVmODViZ2ouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjE0NTU1MTY0NTksImV4cCI6MTQ1NTUyMDA1OX0.dRmPcE-lfGvue1CTYZQbDfQe8-fsScEt22BWU0D6equmlNxddpRyAkl0tf68T4YTBgQ6qDJa5-ebJDZN3Qx7fU7IYop49egzvYDJK0p-rQKO8pIPnmKMVJYRwKtY9hQtX8h32smsvoZMeLfpyf1Xwzn7lpgY39f9w8hQ2PTgowbKfUAb9pkEByQs5p-4gb_WAvsr4bygqV2mhj-y0PbOET15kG003Oz4_O_tgqX8pFFEQxEY_8VVDhs_tZ0D66s07smBwZ6WJC8cCFLV-epi2EMYhEL4gkFVFU7Aaj0ZDlRRNzIs71C_gjj-dx-G8p9bPrg14BPtBxpz8zSBuGyu2A"}, "client_id": "255555110806-4lk2mou3oek0hk7l9rpnegaqaef85bgj.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v2/tokeninfo", "client_secret": "071WJgVZK-Rzb7bHyoHn28ao", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/fxyAKw-rmpmHD9AEsJrC-9NP7Tt_aHI4-M028GwYvNBIgOrJDtdun6zK6XiATCKT", "user_agent": null}')
    credentials = OAuth2Credentials.from_json(engineer_creds[engineer])
    credentials.refresh(httplib2.Http())
    return credentials

def build_flow():
    SCOPES = ['https://www.googleapis.com/auth/plus.me',
      'https://www.googleapis.com/auth/plus.stream.write',
      'https://www.googleapis.com/auth/plus.stream.read',
      'https://www.googleapis.com/auth/plus.circles.write',
      'https://www.googleapis.com/auth/plus.circles.read']

    REDIRECT_URI = 'http://gp-test-1.appspot.com/auth/callback'

    CLIENT_ID = '255555110806-5d85l89k5c6ofdihp6fcflit86foatfc.apps.googleusercontent.com'
    CLIENT_SECRET = '1kk1vYbu8hKBz_GxYjJl6Frm'

    flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                       client_secret=CLIENT_SECRET,
                       scope=SCOPES,
                       redirect_uri=REDIRECT_URI)
    return flow

def build_service(engineer):
    credentials = refresh_token(engineer.lower())
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('plusDomains', 'v1', http=http)

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

class AuthCallbackHandler(webapp2.RequestHandler):
    def get(self):
        code = self.request.get('code')
        flow = build_flow()
        credentials = flow.step2_exchange(code)
        self.response.write(credentials.to_json())

class AuthHandler(webapp2.RequestHandler):
    def get(self):
        flow = build_flow()
        auth_uri = flow.step1_get_authorize_url()
        self.redirect(auth_uri)

class GetTicketHandler(webapp2.RequestHandler):
    def get_people(self, circle_id):
        people = self.service.people().listByCircle(circleId=circle_id).execute()
        children = []
        response ={"name":"people","children":children}
        for child in people["items"]:
            curr_child = {"name":child["displayName"],
                     "size":3938,
                     "image":child["image"]["url"].replace("?sz=50", "?sz=500"),
                     "profile":child["url"]
                   }
            children.append(curr_child)
        return response

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
        job_id = self.request.get('job_id')
        response = {}
        if job_id:
            t = Ticket.all().filter('job_id', job_id).get()
        else:
            t = Ticket.all().filter('assigned', False).get()
        if t:
            t.assigned = True
            t.put()
            LastAssignedTicket(key_name="1", ticket=t).put()
        else:
            lastAssignedTicket = LastAssignedTicket.get_by_key_name('1')
            if lastAssignedTicket:
                t = lastAssignedTicket.ticket
        self.service = build_service(t.engineer[1])
        notes = []
        for note_id in t.note_ids:
            notes.append(self.read_note(note_id))
        response = {'id': t.key().id(), 'job_id': t.job_id, 'customer': t.customer, 'people': self.get_people(t.circle_id), 'engineer': t.engineer, 'lat': t.location.lat, 'lon': t.location.lon, 'documents': [self.get_document(document_id) for document_id in t.document_ids] , 'location_text': t.location_text, 'location': str(t.location), 'issue_type': t.issue_type, 'equipments': t.equipments, 'services': t.services, 'notes': notes}
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
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
    def get_people_set(self, people):
        retVal = set()
        roles = ['experts', 'engineers']
        for role in roles:
            if role in people:
                for person in people[role]:
                    retVal.add(person[1])
        return retVal

    def extend(self, people, tag_people):
        roles = ['experts', 'engineers']
        people_set = self.get_people_set(people)
        for role in roles:
            if role in tag_people:
                parent_list = []
                if role in people:
                    parent_list = people[role]
                else:
                    people[role] = parent_list
                for person in tag_people[role]:
                    if person[1] not in people_set:
                        people_set.add(person[1])
                        parent_list.append(person)

    def get(self):
        tag = self.request.get('tag')
        people = {}
        if tag != '-1':
            tag_people = tags_to_people[tag]
            people = tag_people
        notes = self.request.get('notes').lower()
        for curr_tag in tags:
            if curr_tag in notes:
                tag_people = tags_to_people[curr_tag]
                self.extend(people, tag_people)
        self.response.write(json.dumps(people))

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
        job_id = self.request.get('job-id')
        equipments = self.request.get('equipments').split('#$#')
        services = self.request.get('services').split('#$#')
        location = GeoPt(lat, lng)
        location_text = self.request.get('location_text')
        customer = self.request.get('customer').split(',')
        engineer = self.request.get('engineer').split(',')
        ticket = Ticket(job_id=job_id, customer=customer, engineer=engineer, location=location, location_text=location_text, assigned=assigned, issue_type=issue_type, equipments=equipments, services=services)
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
        engineer = self.request.get('engineer').split(',')[0]
        engineer_name = self.request.get('engineer').split(',')[1]
        self.service = build_service(engineer_name)
        notes = self.request.get('notes').split('#$#')
        note_ids = []
        ticket_id = self.create_ticket()
        circle_id = self.create_circle(ticket_id)
        document_ids = [self.create_documents(d.split(' :: ')[0], d.split(' :: ')[1], circle_id) for d in self.request.get('documents').split('#$#')]
        for note in notes:
            note_ids.append(self.create_note(note, circle_id))
        self.update_ticket(ticket_id, circle_id, note_ids, document_ids)
        engineer = self.request.get('engineer').split(',')[0]
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

class JobDeetsHandler(webapp2.RequestHandler):
    def get(self):
        deets = job_id_map[self.request.get('job-id')]
        self.response.out.write(json.dumps(deets))

app = webapp2.WSGIApplication([
                                ('/', MainPage),
                                ('/auth', AuthHandler),
                                ('/auth/callback', AuthCallbackHandler),
                                ('/tickets/get', GetTicketHandler),
                                ('/circles/get', GetCirclesHandler),
                                ('/circles/assign', AssignCirclesHandler),
                                ('/notes/create', CreateNoteHandler),
                                ('/notes/get', GetNotesHandler),
                                ('/people/get', GetPeopleHandler),
                                ('/tickets/get_people', GetTicketPeopleHandler),
                                ('/tags/get', GetTagsHandler),
                                ('/tickets/create', TempHandler),
                                ('/tickets/get_job_deets', JobDeetsHandler)
                            ], debug=True)