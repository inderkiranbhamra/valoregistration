from flask import Flask, request, jsonify, redirect, url_for, send_file
from flask_cors import CORS  # Import CORS
import yagmail
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import secrets
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for your Flask app

# Set the secret key for the session
app.secret_key = 'inderkiran@24'

# Email configuration
sender_email = 'hackoverflow@cumail.in'  # replace with your email
app_password = 'lgde lflp hmgu krrd'  # replace with your generated app password

# Google Sheets configuration
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('bgmi-registration-e1d0ccd3b338.json', scope)
gc = gspread.authorize(credentials)
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1Y02mNph9lvPE-LmoJ2Ks6BZ4T84_HPF-O1toDIqYe3w/edit#gid=0'
sh = gc.open_by_url(spreadsheet_url)
worksheet = sh.get_worksheet(2)  # Assuming you are working with the first sheet

# Dictionary to store email verification tokens
email_tokens = {}


# Function to generate a random token
def generate_token():
    return secrets.token_hex(16)


# Function to generate an authentication link with token
def generate_auth_link(token, data):
    # Construct the authentication link with modified parameters
    auth_link = f'https://bgmiregistration.vercel.app/verify/{token}?'
    for key, value in data.items():
        auth_link += f'{key}={value}&'
    return auth_link[:-1]


# Route to handle form submission and send authentication email
@app.route('/submit', methods=['POST'])
def send_email():
    if request.method == 'POST':
        data = request.get_json()
        token = generate_token()
        email = data['leader_email']  # Assuming leader's email is used for verification
        email_tokens[email] = token

        # Construct authentication link with all required parameters
        auth_link = generate_auth_link(token, data)
        subject = 'Authentication Link'
        body = f'''
                <html>
                <head>
                    <title>{subject}</title>
                </head>
                <body>
                    <h2>{subject}</h2>
                    <p>Click the button below to authenticate:</p>
                    <a href="{auth_link}" >Authenticate</a>
                </body>
                </html>
                '''

        # Create yagmail SMTP client
        yag = yagmail.SMTP(sender_email, app_password)

        # Send the email
        yag.send(to=email, subject=subject, contents=body)

        return redirect(url_for('email_sent'))


# Route to inform user that email has been sent
@app.route('/email_sent')
def email_sent():
    return send_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'email_sent.html'))


# Route to handle verification
@app.route('/verify/<token>', methods=['GET'])
def verify(token):
    if token:
        # Check if the token exists in email_tokens
        if token in email_tokens.values():
            # Get the email associated with the token
            email = [key for key, value in email_tokens.items() if value == token][0]

            # Retrieve data from the query parameters
            data = request.args.to_dict()

            # Check if all required parameters are present
            required_fields = ['team_name', 'college_name', 'leader_name', 'leader_ign', 'leader_discord_tag',
                               'leader_rank', 'leader_contact', 'leader_email', 'p2_name', 'p2_ign', 'p2_discord_tag',
                               'p2_rank', 'p2_contact', 'p2_email', 'p3_name', 'p3_ign', 'p3_discord_tag', 'p3_rank',
                               'p3_contact', 'p3_email', 'p4_name', 'p4_ign', 'p4_discord_tag', 'p4_rank',
                               'p4_contact', 'p4_email']

            if all(field in data for field in required_fields):
                # Append new data to Google Sheets
                new_row = [data[field] for field in required_fields]
                worksheet.append_row(new_row)
                # Remove token from dictionary after verification
                del email_tokens[email]
                return jsonify({'message': 'Authentication successful. Data stored into Google Sheets.'})
            else:
                return jsonify({'message': 'Missing parameters in the verification link.'}), 400
        else:
            return jsonify({'message': 'Invalid or expired verification link.'}), 400
    else:
        return jsonify({'message': 'No token provided.'}), 400
