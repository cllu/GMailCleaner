from os import getenv

from flask import Flask

from .api import (
    AuthAPI,
    AuthCallbackAPI,
    MessagesAPI,
)


app = Flask(__name__)

app.config['GOOGLE_CLIENT_ID'] = getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = getenv('GOOGLE_CLIENT_SECRET')

# API endpoints
app.add_url_rule('/api/auth/', view_func=AuthAPI.as_view('auth'))
app.add_url_rule('/api/auth/callback/', view_func=AuthCallbackAPI.as_view('callback'))
app.add_url_rule('/api/messages/', view_func=MessagesAPI.as_view('messages'))


# Angular routes
@app.route('/')
@app.route('/auth/')
@app.route('/auth/callback/')
@app.route('/app/')
def index():
    return app.send_static_file('index.html')
