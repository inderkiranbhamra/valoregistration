from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yagmail
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import secrets
import os

app = Flask(__name__)
CORS(app)

app.secret_key = 'inderkiran@24'

sender_email = 'hackoverflow@cumail.in'
app_password = 'lgde lflp hmgu krrd'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('bgmi-registration-e1d0ccd3b338.json', scope)
gc = gspread.authorize(credentials)
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1Y02mNph9lvPE-LmoJ2Ks6BZ4T84_HPF-O1toDIqYe3w/edit#gid=0'
sh = gc.open_by_url(spreadsheet_url)
worksheet = sh.sheet1

email_tokens = {}


def generate_token():
    return secrets.token_hex(16)


def generate_auth_link(token, data):
    auth_link = f'https://valoregistration2.vercel.app/verify/{token}'
    for key, value in data.items():
        auth_link += f"&{key}={value.replace(' ', '_')}"
    return auth_link


@app.route('/submit', methods=['POST'])
def send_email():
    if request.method == 'POST':
        data = request.json
        token = generate_token()
        email = data.get('leader_email')

        email_tokens[email] = token

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

        yag = yagmail.SMTP(sender_email, app_password)

        yag.send(to=email, subject=subject, contents=body)

        return jsonify({'message': 'Email sent successfully.'})


@app.route('/email_sent')
def email_sent():
    return send_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'email_sent.html'))


@app.route('/verify/<token>', methods=['GET'])
def verify(token):
    if token:
        if token in email_tokens.values():
            email = [key for key, value in email_tokens.items() if value == token][0]
            data = request.args.to_dict()

            if all(data.values()):
                new_row = [data[key] for key in sorted(data.keys())]
                worksheet.append_row(new_row)
                del email_tokens[email]
                return jsonify({'message': 'Authentication successful. Data stored into Google Sheets.'})
            else:
                return jsonify({'message': 'Missing parameters in the verification link.'}), 400
        else:
            return jsonify({'message': 'Invalid or expired verification link.'}), 400
    else:
        return jsonify({'message': 'No token provided.'}), 400
