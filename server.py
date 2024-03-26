from flask import Flask, render_template, request, redirect, url_for, session
import os
import random
import string
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import id_token
from google.auth.transport import requests
from werkzeug.utils import secure_filename
import PyPDF2
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'ShishirSadmanAshrif'
CLIENT_ID = '800694117086-erlqhno10ehmn3n7q4sq4hsvha7ifsgm.apps.googleusercontent.com'

# Configure file upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATABASE = 'pdf_data.db'

# Function to create SQLite database and table
def create_table():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pdf_files (id INTEGER PRIMARY KEY, filename TEXT, content TEXT)''')
    conn.commit()
    conn.close()

# Function to insert PDF data into database
def insert_pdf(filename, content):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO pdf_files (filename, content) VALUES (?, ?)", (filename, content))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return redirect('https://accounts.google.com/o/oauth2/auth?response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fcallback&client_id={}&scope=email&access_type=offline'.format(CLIENT_ID))


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
    session['user_name'] = id_info.get('name', 'Unknown')

    return redirect(url_for('input_page'))

@app.route('/input', methods=['GET', 'POST'])
def input_page():
    if request.method == 'POST':
        # Handle form submission
        
        # Extract form data
        sheet_questions = request.form['sheet_questions']
        sheet_students = request.form['sheet_students']
        deadline = request.form['deadline']
        
        # Upload PDF file
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Read PDF content and store in database
            content = extract_pdf_text(pdf_path)
            insert_pdf(filename, content)

        # Call function similar to the one in Google Apps Script
        create_form_and_send_email(sheet_questions, sheet_students, deadline)

        return 'Form created and email sent successfully!'

    else:
        # Render input page template
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

# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to extract text from PDF file
def extract_pdf_text(file_path):
    content = ''
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        num_pages = reader.numPages
        for page_number in range(num_pages):
            page = reader.getPage(page_number)
            content += page.extractText()
    return content

@app.route('/continue', methods=['POST'])
def continue_clicked():
    student_sheet_url = request.form['studentSheetUrl']
    question_sheet_url = request.form['questionSheetUrl']
    deadline_date = request.form['deadlineDate']

    # Check if fields are non-empty
    if student_sheet_url and question_sheet_url and deadline_date:
        # Log values to console
        print("Student Sheet URL:", student_sheet_url)
        print("Question Sheet URL:", question_sheet_url)
        print("Deadline Date:", deadline_date)

        # Call the function similar to the one in Google Apps Script
        create_form_and_send_email(question_sheet_url, student_sheet_url, deadline_date)

        return "Form has been Sent Successfully"
    else:
        return "Please fill in all fields."
    
def create_form_and_send_email(question_sheet_url, student_sheet_url, deadline_date):
    # Connect to Google Sheets API
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('sheets', 'v4', credentials=creds)
    client = gspread.authorize(creds)

    # Open the Google Sheets by URL
    questions_sheet = client.open_by_url(question_sheet_url)
    students_sheet = client.open_by_url(student_sheet_url)

    # Get questions from the first column of the questions sheet
    questions = questions_sheet.sheet1.col_values(1)

    # Get emails from the third column of the students sheet
    emails = students_sheet.sheet1.col_values(3)

    # Create a new Google Form
    form = service.forms().create(body={'title': 'Project Form', 'description': 'Please fill out the form'}).execute()
    
    # Add questions to the form
    for question in questions:
        service.forms().addTextItem(formId=form['formId'], body={'title': question, 'helpText': 'Please provide your answer'}).execute()

    # Get the form URL
    form_url = f"https://docs.google.com/forms/d/{form['formId']}/viewform"

    # Send the form link to students via email along with the deadline
    deadline_time = datetime.strptime(deadline_date, '%Y-%m-%dT%H:%M:%S.%f')
   # Convert string to datetime object
    for email in emails:
        message = f"Dear student,\n\nHere is the link to the form: {form_url}\n\nDeadline for submission: {deadline_time}"
        send_email(email, message)

def send_email(receiver_email, message, credentials):
    # Connect to Google Gmail API
    service = build('gmail', 'v1', credentials=credentials)

    # Create a new message
    message = MIMEMultipart()
    message['to'] = receiver_email
    message['subject'] = "Project Form"

    # Create the body of the email
    message.attach(MIMEText(message, 'plain'))

    # Send the email using the Google Gmail API
    try:
        created_message = service.users().messages().send(userId="me", body=message).execute()
        print(f"Email sent to: {receiver_email}")
    except Exception as e:
        print("Error sending email:", e)


if __name__ == '__main__':
    app.run(debug=True)
