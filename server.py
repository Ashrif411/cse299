from flask import Flask, render_template, redirect, url_for, session, request
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)
app.secret_key = 'ShishirSadmanAshrif'
CLIENT_ID = '800694117086-erlqhno10ehmn3n7q4sq4hsvha7ifsgm.apps.googleusercontent.com'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return redirect('https://accounts.google.com/o/oauth2/auth?response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fcallback&client_id={}&scope=email%20profile&access_type=offline'.format(CLIENT_ID))

import requests
from google.auth.transport.requests import Request as GoogleAuthRequest
@app.route('/callback')
def callback():
    code = request.args.get('code')
    # Exchange code for tokens
    token_response = requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': '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',
        'redirect_uri': 'http://localhost:5000/callback',
        'grant_type': 'authorization_code'
    })
    token_data = token_response.json()
    id_token_str = token_data['id_token']
    id_info = id_token.verify_oauth2_token(id_token_str, GoogleAuthRequest(), CLIENT_ID)

    # Store user data in session or database
    session['user_email'] = id_info['email']
    session['user_name'] = id_info.get('name', None) # Set it to None initially

    # Fetch user's name from Google profile if not available in ID token
    if session['user_name'] is None:
        user_info_response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', params={'access_token': token_data['access_token']})
        user_info = user_info_response.json()
        session['user_name'] = user_info.get('name', 'Unknown')

    return redirect(url_for('input_page'))

@app.route('/input')
def input_page():
    user_email = session.get('user_email')
    user_name = session.get('user_name', 'Unknown')
    if user_email:
        return render_template('input.html', user_name=user_name, user_email=user_email)
    else:
        return redirect(url_for('index'))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
