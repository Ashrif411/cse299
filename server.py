from flask import Flask, render_template, redirect, url_for, session, request
from google.oauth2 import id_token
from google.auth.transport import requests
import requests
import base64
from google.auth.transport.requests import Request as GoogleAuthRequest
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import session
import gspread
from google.auth.exceptions import DefaultCredentialsError
from google.auth.credentials import Credentials
from google.auth.exceptions import DefaultCredentialsError
from google.auth import impersonated_credentials
from google.oauth2 import service_account
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

app = Flask(__name__)
app.secret_key = 'ShishirSadmanAshrif'
CLIENT_ID = '800694117086-erlqhno10ehmn3n7q4sq4hsvha7ifsgm.apps.googleusercontent.com'

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['assignment_db']
pdf_collection = db['pdf_files']

# Google Sheets setup
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
try:
    credentials = service_account.Credentials.from_service_account_file('credentials.json', scopes=scope)
except DefaultCredentialsError:
    credentials = None  # or handle the error accordingly
gs_client = gspread.authorize(credentials)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return redirect('https://accounts.google.com/o/oauth2/auth?response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fcallback&client_id={}&scope=email&access_type=offline'.format(CLIENT_ID))

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
    session['user_name'] = id_info.get('name', 'Unknown')
    # Store the OAuth token in session
    session['oauth_token'] = token_data['access_token']

    return redirect(url_for('input_page'))

# Define a function to retrieve the OAuth token from the session
def get_oauth_token():
    return session.get('oauth_token')


@app.route('/input', methods=['POST'])
def input_page():
    user_email = session.get('user_email')
    user_name = session.get('user_name', 'Unknown')
    if user_email:
        # Extract questions from the first column of the question sheet URL
        questions = extract_questions_from_url(request.form['questionSheetUrl'])

        # Extract student emails from the third column of the student sheet URL
        student_emails = extract_emails_from_url(request.form['studentSheetUrl'])

        # Create Google Forms using the extracted questions
        form_url = create_google_form(questions)

        # Mail the forms to student emails
        oauth_token = get_oauth_token()  # You need to implement a function to retrieve the OAuth token
        mail_forms_to_students(form_url, student_emails, user_email, oauth_token)

        # Store the PDF file in the database
        pdf_file = request.files['pdfFile']
        store_pdf_in_database(pdf_file, user_email)

        return render_template('input.html', user_name=user_name, user_email=user_email)
    else:
        return redirect(url_for('index'))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

def extract_questions_from_url(question_sheet_url):
    sheet = gs_client.open_by_url(question_sheet_url).sheet1
    questions = sheet.col_values(1)
    return questions

def extract_emails_from_url(student_sheet_url):
    sheet = gs_client.open_by_url(student_sheet_url).sheet1
    emails = sheet.col_values(3)
    return emails

def create_google_form(questions):
    # Create a new Chrome session
    driver = webdriver.Chrome()
    driver.get("https://docs.google.com/forms")

    # Wait for the page to load
    time.sleep(5)

    # Click on the Blank Form template
    blank_form_button = driver.find_element(By.XPATH, "//div[@aria-label='Blank']")
    blank_form_button.click()

    # Wait for the form editor to load
    time.sleep(5)

    # Input form title
    form_title_input = driver.find_element(By.XPATH, "//input[@aria-label='Form title']")
    form_title_input.send_keys("Assignment Form")

    # Add questions
    for question_text in questions:
        add_question_button = driver.find_element(By.XPATH, "//div[@aria-label='Add question']")
        add_question_button.click()

        time.sleep(1)

        question_input = driver.find_element(By.XPATH, "//textarea[@aria-label='Question']")
        question_input.send_keys(question_text)

        time.sleep(1)

    # Get form URL
    form_url = driver.current_url

    # Close the browser
    driver.quit()

    return form_url

def mail_forms_to_students(form_url, student_emails, user_email):
    for email in student_emails:
        msg = MIMEMultipart()
        msg['From'] = session.get('user_email')
        msg['To'] = email
        msg['Subject'] = 'Google Form for Assignment'
        body = f'Hi,\n\nPlease fill out the following form for your assignment: {form_url}'
        msg.attach(MIMEText(body, 'plain'))

        url = f'https://www.googleapis.com/gmail/v1/users/{session.get("user_email")}/messages/send'
        headers = {
            'Authorization': f'Bearer {oauth_token}',
            'Content-Type': 'message/rfc822'
        }
        raw_message = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}

        response = requests.post(url, headers=headers, json=raw_message)
        if response.status_code != 200:
            print(f"Failed to send email to {email}. Status code: {response.status_code}")
        # Optionally, you could raise an exception or log the failure for further investigation
        # raise Exception(f"Failed to send email to {email}. Status code: {response.status_code}")
        # logger.error(f"Failed to send email to {email}. Status code: {response.status_code}")
        else:
            print(f"Email sent successfully to {email}.")


def store_pdf_in_database(pdf_file, user_email):
    file_id = pdf_collection.insert_one({'user_email': user_email, 'pdf_file': pdf_file.read()}).inserted_id
    return file_id
                                                                  