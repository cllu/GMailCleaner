import requests
from flask import redirect, jsonify, request, current_app
from flask.views import MethodView

from .gmail import GoogleOAuth, GMail


class AuthAPI(MethodView):

    def get(self):
        """
        """
        google_oauth = GoogleOAuth(
            client_id=current_app.config['GOOGLE_CLIENT_ID'],
            client_secret=current_app.config['GOOGLE_CLIENT_SECRET']
        )
        auth_url = google_oauth.get_authorization_url()
        return redirect(auth_url)


class AuthCallbackAPI(MethodView):

    def get(self):
        """
        """
        if 'error' in request.args or 'code' not in request.args:
            return jsonify({
                'error': request.args['error']
            })
        code = request.args.get('code')

        google_oauth = GoogleOAuth(
            client_id=current_app.config['GOOGLE_CLIENT_ID'],
            client_secret=current_app.config['GOOGLE_CLIENT_SECRET']
        )
        access_token, email = google_oauth.request_access_token(code)
        response = current_app.make_response(jsonify({
            'email': email
        }))
        response.set_cookie('access_token', value=access_token, httponly=True)
        response.set_cookie('email', value=email)
        return response


class MessagesAPI(MethodView):

    def get(self):
        """
        """
        # return details by default
        with_details = request.args.get('with_details')
        if with_details is None:
            with_details = True

        q = request.args.get('q')
        if not q:
            return jsonify({
                'message': 'q is not found'
            }), 400

        max_results = request.args.get('max_results') or 10

        access_token = request.cookies.get('access_token')
        if access_token is None:
            return jsonify({
                'message': 'no access_token'
            }), 400

        endpoint = 'https://www.googleapis.com/gmail/v1/users/me/messages'
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        params = {
            'q': q,
            'maxResults': max_results,
        }
        resp = requests.get(endpoint, params=params, headers=headers)
        data = resp.json()
        if 'error' in data:
            message = data.get('error', {}).get('message', None) or 'error when requesting messages'
            return jsonify({
                'response': data,
                'message': message,
            }), 400

        total = data['resultSizeEstimate']
        messages = data.get('messages', [])

        ids = [message['id'] for message in messages]
        messages = GMail(access_token=access_token).batch_get_messages(ids)

        return jsonify({
            'messages': messages,
            'total': total,
        })

    def delete(self):
        """

        """
        access_token = request.cookies.get('access_token')
        if access_token is None:
            return jsonify({
                'error': 'no access_token'
            })

        data = request.get_json(force=True)
        message_ids = data.get('ids')

        num_deleted = GMail(access_token=access_token).delete_messages(message_ids)

        return jsonify({
            'success': True,
            'num_deleted': num_deleted,
        })

