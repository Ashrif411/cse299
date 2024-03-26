# from flask import Flask, render_template, redirect, url_for, session, request
# from google.oauth2 import id_token
# from google.auth.transport import requests
# import requests as flask_requests
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import pandas as pd
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email import encoders
# import os
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# app.secret_key = 'ShishirSadmanAshrif'
# CLIENT_ID = '800694117086-erlqhno10ehmn3n7q4sq4hsvha7ifsgm.apps.googleusercontent.com'

# # Function to create Google Form
# def create_google_form(questions):
#     # Initialize credentials and authorize Google Sheets API
#     scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#     creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
#     client = gspread.authorize(creds)

#     # Create a new Google Sheet
#     form_sheet = client.create('Google Form')
#     sheet = form_sheet.sheet1

#     # Add questions to the sheet
#     for i, question in enumerate(questions):
#         sheet.update_cell(i + 1, 1, question)

#     # Construct and return the form URL
#     form_url = f"https://docs.google.com/forms/d/{form_sheet.id}/edit"
#     return form_url

# # Function to send forms to emails
# def send_forms(emails, form_url, deadline, user_email):
#     try:
#         sender_email = user_email  # Using the user's email obtained from OAuth
#         sender_password = session['user_password']  # Assuming you're storing user's password in session

#         for email in emails:
#             # Create message
#             msg = MIMEMultipart()
#             msg['From'] = sender_email
#             msg['To'] = email
#             msg['Subject'] = "Google Form Invitation"

#             body = f"Dear Student,\n\nPlease fill out the following form before the deadline: {form_url}\n\nDeadline: {deadline}\n\nBest regards,\n[Your Organization]"

#             msg.attach(MIMEText(body, 'plain'))

#             # Send email
#             with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#                 server.login(sender_email, sender_password)
#                 server.send_message(msg)

#         print("Forms sent successfully!")
#     except Exception as e:
#         print(f"Error sending forms: {str(e)}")

# # Function to store PDF file in a directory
# def store_pdf(pdf_file):
#     try:
#         if pdf_file:
#             # Ensure the 'pdf_files' directory exists
#             if not os.path.exists('pdf_files'):
#                 os.makedirs('pdf_files')

#             # Save the PDF file to the 'pdf_files' directory
#             filename = secure_filename(pdf_file.filename)
#             pdf_file.save(os.path.join('pdf_files', filename))
#             print("PDF file stored successfully!")
#         else:
#             print("No PDF file provided.")
#     except Exception as e:
#         print(f"Error storing PDF file: {str(e)}")
# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/login')
# def login():
#     return redirect('https://accounts.google.com/o/oauth2/auth?response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fcallback&client_id={}&scope=email&access_type=offline'.format(CLIENT_ID))

# @app.route('/callback')
# def callback():
#     code = request.args.get('code')
#     # Exchange code for tokens
#     token_response = flask_requests.post('https://oauth2.googleapis.com/token', data={
#     'code': code,
#     'client_id': CLIENT_ID,
#     'client_secret': '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',
#     'redirect_uri': 'http://localhost:5000/callback',
#     'grant_type': 'authorization_code'
#     })

#     token_data = token_response.json()
#     id_token_str = token_data['id_token']
#     id_info = id_token.verify_oauth2_token(id_token_str, requests.Request(), CLIENT_ID)

#     # Store user data in session or database
#     session['user_email'] = id_info['email']
#     session['user_name'] = id_info.get('name', 'Unknown')

#     return redirect(url_for('input_page'))

# @app.route('/input')
# def input_page():
#     user_email = session.get('user_email')
#     user_name = session.get('user_name', 'Unknown')
#     if user_email:
#         return render_template('input.html', user_name=user_name, user_email=user_email)
#     else:
#         return redirect(url_for('index'))

# @app.route('/process_form', methods=['POST'])
# def process_form():
#     student_sheet_url = request.form['studentSheetUrl']
#     questions_sheet_url = request.form['questionsSheetUrl']
#     deadline_date = request.form['deadlineDate']
#     pdf_file = request.files['pdfFile']

#     # Extract questions from the questions sheet URL
#     scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#     credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
#     client = gspread.authorize(credentials)
#     questions_sheet = client.open_by_url(questions_sheet_url).sheet1
#     questions = questions_sheet.col_values(1)

#     # Create Google Form
#     form_url = create_google_form(questions)

#     # Extract emails from student sheet URL
#     student_sheet = client.open_by_url(student_sheet_url).sheet1
#     emails = student_sheet.col_values(3)

#     # Send forms to emails
#     send_forms(emails, form_url, deadline_date)

#     # Store PDF file in database
#     store_pdf(pdf_file)

#     return "Form creation and email sending process completed successfully!"

# @app.route('/logout', methods=['POST'])
# def logout():
#     session.clear()
#     return redirect(url_for('index'))

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, redirect, url_for, session, request
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as flask_requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ShishirSadmanAshrif'
CLIENT_ID = '800694117086-erlqhno10ehmn3n7q4sq4hsvha7ifsgm.apps.googleusercontent.com'

# Function to create Google Form
def create_google_form(questions):
    # Initialize credentials and authorize Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)

    # Create a new Google Sheet
    form_sheet = client.create('Google Form')
    sheet = form_sheet.sheet1

    # Batch update cells to add questions to the sheet
    batch_update = []
    for i, question in enumerate(questions):
        batch_update.append({
            'range': f'A{i + 1}:A{i + 1}',
            'values': [[question]]
        })

    sheet.batch_update(batch_update)

    # Construct and return the form URL
    form_url = f"https://docs.google.com/forms/d/{form_sheet.id}/edit"
    return form_url

def send_forms(emails, form_url, deadline, oauth_token, user_email):
    try:
        for email in emails:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = user_email
            msg['To'] = email
            msg['Subject'] = "Google Form Invitation"

            body = f"Dear Student,\n\nPlease fill out the following form before the deadline: {form_url}\n\nDeadline: {deadline}\n\nBest regards,\n[Your Organization]"

            msg.attach(MIMEText(body, 'plain'))

            # Send email using OAuth token
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.ehlo()
                server.login(user_email, oauth_token)
                server.send_message(msg)

        print("Forms sent successfully!")
    except Exception as e:
        print(f"Error sending forms: {str(e)}")


# Function to store PDF file in a directory
def store_pdf(pdf_file):
    try:
        if pdf_file:
            # Ensure the 'pdf_files' directory exists
            if not os.path.exists('pdf_files'):
                os.makedirs('pdf_files')

            # Save the PDF file to the 'pdf_files' directory
            filename = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join('pdf_files', filename))
            print("PDF file stored successfully!")
        else:
            print("No PDF file provided.")
    except Exception as e:
        print(f"Error storing PDF file: {str(e)}")

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
    token_response = flask_requests.post('https://oauth2.googleapis.com/token', data={
    'code': code,
    'client_id': CLIENT_ID,
    'client_secret': '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',
    'redirect_uri': 'http://localhost:5000/callback',
    'grant_type': 'authorization_code'
    })

    token_data = token_response.json()
    id_token_str = token_data['id_token']
    id_info = id_token.verify_oauth2_token(id_token_str, requests.Request(), CLIENT_ID)

    # Store user data in session or database
    session['user_email'] = id_info['email']
    session['user_name'] = id_info.get('name', 'Unknown')

    return redirect(url_for('input_page'))

@app.route('/input')
def input_page():
    user_email = session.get('user_email')
    user_name = session.get('user_name', 'Unknown')
    if user_email:
        return render_template('input.html', user_name=user_name, user_email=user_email)
    else:
        return redirect(url_for('index'))

@app.route('/process_form', methods=['POST'])
def process_form():
    student_sheet_url = request.form['studentSheetUrl']
    questions_sheet_url = request.form['questionsSheetUrl']
    deadline_date = request.form['deadlineDate']
    pdf_file = request.files['pdfFile']

    # Extract questions from the questions sheet URL
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(credentials)
    questions_sheet = client.open_by_url(questions_sheet_url).sheet1
    questions = questions_sheet.col_values(1)

    # Create Google Form
    form_url = create_google_form(questions)

    # Extract emails from student sheet URL
    student_sheet = client.open_by_url(student_sheet_url).sheet1
    emails = student_sheet.col_values(3)

    # Send forms to emails using OAuth token
    send_forms(emails, form_url, deadline_date, session.get('oauth_token'), session.get('user_email'))

    # Store PDF file in database
    store_pdf(pdf_file)

    return "Form creation and email sending process completed successfully!"

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
