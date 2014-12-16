import json
from urllib.parse import urlencode

import jwt
from flask import jsonify
import requests

from .utils import chunks


class GoogleOAuth:
    redirect_uri = 'https://gmail-cleaner.herokuapp.com/auth/callback/'
    token_request_uri = "https://accounts.google.com/o/oauth2/auth"
    access_token_uri = 'https://accounts.google.com/o/oauth2/token'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_authorization_url(self):
        scope = ' '.join([
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/gmail.modify',
            ])
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': scope,
            }
        url = self.token_request_uri + '?' + urlencode(params)
        return url

    def request_access_token(self, authorization_code):
        data = {
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            }
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        resp = requests.post(self.access_token_uri, data=data, headers=headers)
        token_data = resp.json()

        # TODO: exception
        if 'error' in token_data:
            return jsonify({
                'success': False,
                'error': token_data,
                })
        access_token = token_data['access_token']
        id_token = jwt.decode(token_data['id_token'], verify=False)
        email = id_token['email']

        return access_token, email


class GMail:

    def __init__(self, access_token):
        self.access_token = access_token

    def get_message(self, message_id):
        """
        """
        endpoint = 'https://www.googleapis.com/gmail/v1/users/me/messages/%s' % message_id
        params = {
            'format': 'metadata',
        }
        headers = {
            'Authorization': 'Bearer ' + self.access_token
        }
        resp = requests.get(endpoint, params=params, headers=headers)
        data = resp.json()

        sender = None
        receiver = None
        subject = None
        for header in data['payload']['headers']:
            if header['name'] == 'From':
                sender = header['value']
            elif header['name'] == 'To':
                receiver = header['value']
            elif header['name'] == 'Subject':
                subject = header['value']

        return {
            'sender': sender,
            'receiver': receiver,
            'subject': subject,
        }

    def delete_message(self, message_id):
        """
        """
        endpoint = 'https://www.googleapis.com/gmail/v1/users/me/messages/%s/trash' % message_id
        headers = {
            'Authorization': 'Bearer ' + self.access_token
        }
        resp = requests.post(endpoint, headers=headers)
        return {
            'success': True,
            'resp': resp,
        }

    def get_messages(self, message_ids):
        messages = []
        for chunk in chunks(message_ids, 100):
            messages.extend(self.batch_get_messages(chunk))
        return messages

    def batch_get_messages(self, message_ids):
        """
        Batch requests: https://developers.google.com/gmail/api/guides/batch
        """
        endpoint = 'https://www.googleapis.com/batch'
        boundary = 'batch_boundary'
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'multipart/mixed; boundary=%s' % boundary,
        }

        body = ''
        for message_id in message_ids:
            req = 'GET /gmail/v1/users/me/messages/%s?format=metadata&metadataHeaders=From&metadataHeaders=To&metadataHeaders=Subject&metadataHeaders=Date' % message_id
            body += '--%s\n' % boundary
            body += 'Content-Type: application/http\n\n'
            body += '%s\n\n' % req

        # end boundary
        body += '--%s--' % boundary

        response = requests.post(endpoint, data=body.encode(encoding='utf-8'), headers=headers)
        # the response does not use our requested boundary
        boundary = response.headers['Content-Type'][len('multipart/mixed; boundary='):]

        # remove the end boundary first
        text = response.text.replace('--%s--' % boundary, '')

        # parse batch response
        messages = []
        chunks = [c for c in text.split('--' + boundary) if c]
        for chunk in chunks:
            lines = [l for l in chunk.split('\r\n') if l]
            if len(lines) == 0:
                continue

            data = json.loads(lines[-1])

            message_id = data['id']

            sender = None
            receiver = None
            subject = None
            for header in data['payload']['headers']:
                if header['name'] == 'From':
                    sender = header['value']
                elif header['name'] == 'To':
                    receiver = header['value']
                elif header['name'] == 'Subject':
                    subject = header['value']

            messages.append({
                'id': message_id,
                'sender': sender,
                'receiver': receiver,
                'subject': subject,
            })

        return messages

    def delete_messages(self, message_ids):
        """
        """
        num_deleted = 0
        for chunk in chunks(message_ids, 100):
            num_deleted += self.batch_delete_messages(chunk)

        return num_deleted

    def batch_delete_messages(self, message_ids):
        """
        """
        endpoint = 'https://www.googleapis.com/batch'
        boundary = 'batch_boundary'
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'multipart/mixed; boundary=%s' % boundary,
        }

        body = ''
        for message_id in message_ids:
            req = 'POST /gmail/v1/users/me/messages/%s/trash' % message_id
            body += '--%s\n' % boundary
            body += 'Content-Type: application/http\n\n'
            body += '%s\n\n' % req

        # end boundary
        body += '--%s--' % boundary

        response = requests.post(endpoint, data=body.encode(encoding='utf-8'), headers=headers)
        # the response does not use our requested boundary
        boundary = response.headers['Content-Type'][len('multipart/mixed; boundary='):]

        # remove the end boundary first
        text = response.text.replace('--%s--' % boundary, '')

        # parse batch response
        num_deleted = 0
        chunks = [c for c in text.split('--' + boundary) if c]
        for chunk in chunks:
            lines = [l for l in chunk.split('\r\n') if l]
            if len(lines) == 0:
                continue

            data = json.loads(lines[-1])

            message_id = data.get('id', None)
            if message_id:
                num_deleted += 1

        return num_deleted
