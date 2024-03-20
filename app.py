from flask import Flask, request, jsonify
from flask_cors import CORS
import yagmail
import mysql.connector
import secrets
from urllib.parse import urlencode

app = Flask(__name__)
CORS(app)

app.secret_key = 'inderkiran@24'

# MySQL database configuration
DB_HOST = '217.21.94.103'
DB_NAME = 'u813060526_gameathonregis'
DB_USER = 'u813060526_gameathonregis'
DB_PASSWORD = '135@Hack'

# Connect to the MySQL database
conn = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS UniqueIGNVALO (ign VARCHAR(255) UNIQUE)")
conn.commit()
# cursor.execute("DROP TABLE IF EXISTS UniqueIGN")
# conn.commit()
cursor.execute('''CREATE TABLE IF NOT EXISTS Valoregistrations (
    team_name VARCHAR(255) PRIMARY KEY,
    college_name VARCHAR(255),
    leader_name VARCHAR(255),
    leader_ign VARCHAR(255) UNIQUE,
    leader_game_id VARCHAR(255) UNIQUE,
    leader_id_no VARCHAR(255) UNIQUE,
    leader_contact VARCHAR(255) UNIQUE,
    leader_email VARCHAR(255) UNIQUE,
    p2_name VARCHAR(255),
    p2_ign VARCHAR(255) UNIQUE,
    p2_game_id VARCHAR(255) UNIQUE,
    p2_id_no VARCHAR(255) UNIQUE,
    p2_contact VARCHAR(255) UNIQUE,
    p3_name VARCHAR(255),
    p3_ign VARCHAR(255) UNIQUE,
    p3_game_id VARCHAR(255) UNIQUE,
    p3_id_no VARCHAR(255) UNIQUE,
    p3_contact VARCHAR(255) UNIQUE,
    p4_name VARCHAR(255),
    p4_ign VARCHAR(255) UNIQUE,
    p4_game_id VARCHAR(255) UNIQUE,
    p4_id_no VARCHAR(255) UNIQUE,
    p4_contact VARCHAR(255) UNIQUE,
    p5_name VARCHAR(255),
    p5_ign VARCHAR(255) UNIQUE,
    p5_game_id VARCHAR(255) UNIQUE,
    p5_id_no VARCHAR(255) UNIQUE,
    p5_contact VARCHAR(255) UNIQUE
);
''')
conn.commit()

# Email configuration
sender_email = 'hackoverflow@cumail.in'
app_password = 'lgde lflp hmgu krrd'

email_tokens = {}


def generate_token():
    return secrets.token_hex(16)


def generate_auth_link(token, data):
    auth_link = f'https://valoregistration2.vercel.app/verify/{token}?'
    auth_link += urlencode(data)
    return auth_link

#
# def check_duplicate_email(data):
#     email_set = set()
#     emails = [data['leader_email'], data['p2_email'], data['p3_email'], data['p4_email']]
#     for email in emails:
#         if email in email_set:
#             print("Duplicate email detected:", email)
#             return True
#         else:
#             email_set.add(email)
#
#     for email in emails:
#         cursor.execute("SELECT * FROM UniqueEmails2 WHERE email = %s", (email,))
#         result = cursor.fetchone()
#         if result:
#             print("Duplicate email detected:", email)
#             return True
#
#     return False


# def check_duplicate_ign(data):
#     ign_set = set()
#     igns = [data['team_name'], data['leader_ign'], data['leader_game_id'], data['leader_id_no'], data['leader_contact'], data['leader_email'], data['p2_ign'], data['p2_game_id'], data['p2_id_no'], data['p2_contact'], data['p3_ign'], data['p3_game_id'], data['p3_id_no'], data['p3_contact'], data['p4_ign'], data['p4_game_id'], data['p4_id_no'], data['p4_contact']]
#     for ign in igns:
#         if ign in ign_set:
#             print("Duplicate IGN detected:", ign)
#             return True
#         else:
#             ign_set.add(ign)
#
#     for ign in igns:
#         cursor.execute("SELECT * FROM UniqueIGN WHERE ign = %s", (ign,))
#         result = cursor.fetchone()
#         if result:
#             print("Duplicate ign detected:", ign)
#             return True
#
#     return False

def check_duplicate_ign(data):
    ign_set = set()
    igns = [data['team_name'], data['leader_ign'], data['leader_game_id'], data['leader_id_no'], data['leader_contact'], data['leader_email'], data['p2_ign'], data['p2_game_id'], data['p2_id_no'], data['p2_contact'], data['p3_ign'], data['p3_game_id'], data['p3_id_no'], data['p3_contact'], data['p4_ign'], data['p4_game_id'], data['p4_id_no'], data['p4_contact'], data['p5_ign'], data['p5_game_id'], data['p5_id_no'], data['p5_contact']]
    field_names = ['Team Name', 'Leader IGN', 'Leader Game ID', 'Leader ID Number', 'Leader Contact', 'Leader Email', 'P2 IGN', 'P2 Game ID', 'P2 ID Number', 'P2 Contact', 'P3 IGN', 'P3 Game ID', 'P3 ID Number', 'P3 Contact', 'P4 IGN', 'P4 Game ID', 'P4 ID Number', 'P4 Contact', 'P5 IGN', 'P5 Game ID', 'P5 ID Number', 'P5 Contact']
    duplicate_fields = []

    for i, ign in enumerate(igns):
        if ign in ign_set:
            print("Duplicate IGN detected at field", field_names[i], ":", ign)
            duplicate_fields.append(field_names[i])
        ign_set.add(ign)

    for ign in igns:
        cursor.execute("SELECT * FROM UniqueIGNVALO WHERE ign = %s", (ign,))
        result = cursor.fetchone()
        if result:
            print("Duplicate IGN detected:", ign)
            return True, duplicate_fields, ign

    return False, [], ''


@app.route('/')
def index():
    return 'API is working'


@app.route('/submit', methods=['POST'])
def send_email():
    data = request.get_json()
    token = generate_token()

    # uniqueemails = [data['leader_email'], data['p2_email'], data['p3_email'], data['p4_email']]
    # uniqueigns = [data['leader_ign'], data['p2_ign'], data['p3_ign'], data['p4_ign']]

    # if check_duplicate_email(data):
    #     return jsonify({'message': 'Duplicate email detected.'}), 400

    result, duplicate_fields, duplicate_ign = check_duplicate_ign(data)
    if result:
        if duplicate_fields:
            return jsonify({'message': f'Duplicate data found at {duplicate_fields}: {duplicate_ign}.'}), 400
        else:
            return jsonify({'message': 'Duplicate data detected.'}), 400


    email = data['leader_email']
    email_tokens[email] = token

    auth_link = generate_auth_link(token, data)
    subject = 'Authentication Email for VALO Registration'
    body = f'''
            <html>
            <head>
                <title>{subject}</title>
            </head>
            <body>
                <h2>Click on the link below to complete your registration:</h2>
                <h2><a href="{auth_link}" >Click Here</a><h2>
            </body>
            </html>
            '''

    yag = yagmail.SMTP(sender_email, app_password)
    yag.send(to=email, subject=subject, contents=body)

    return jsonify({'message': 'Email sent successfully.'})


@app.route('/verify/<token>', methods=['GET'])
def verify(token):
    if token in email_tokens.values():
        emails = [key for key, value in email_tokens.items() if value == token][0]
        data = request.args.to_dict()
        # uniqueemails = [data['leader_email'], data['p2_email'], data['p3_email'], data['p4_email']]
        uniqueigns = [data['team_name'], data['leader_ign'], data['leader_game_id'], data['leader_id_no'], data['leader_contact'], data['leader_email'], data['p2_ign'], data['p2_game_id'], data['p2_id_no'], data['p2_contact'], data['p3_ign'], data['p3_game_id'], data['p3_id_no'], data['p3_contact'], data['p4_ign'], data['p4_game_id'], data['p4_id_no'], data['p4_contact'], data['p5_ign'], data['p5_game_id'], data['p5_id_no'], data['p5_contact']]

        try:
            for y in uniqueigns:
                cursor.execute("INSERT INTO UniqueIGNVALO (ign) VALUES (%s)", (y,))
            conn.commit()

            # for x in uniqueemails:
            #     cursor.execute("INSERT INTO UniqueEmails2 (email) VALUES (%s)", (x,))
            # conn.commit()

            cursor.execute("INSERT INTO Valoregistrations (team_name, college_name, leader_name, leader_ign, leader_game_id, leader_id_no, leader_contact, leader_email, p2_name, p2_ign, p2_game_id, p2_id_no, p2_contact, p3_name, p3_ign, p3_game_id, p3_id_no, p3_contact, p4_name, p4_ign, p4_game_id, p4_id_no, p4_contact, p5_name, p5_ign, p5_game_id, p5_id_no, p5_contact) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (data['team_name'], data['college_name'], data['leader_name'], data['leader_ign'], data['leader_game_id'], data['leader_id_no'], data['leader_contact'], data['leader_email'], data['p2_name'], data['p2_ign'], data['p2_game_id'], data['p2_id_no'], data['p2_contact'], data['p3_name'], data['p3_ign'], data['p3_game_id'], data['p3_id_no'], data['p3_contact'], data['p4_name'], data['p4_ign'], data['p4_game_id'], data['p4_id_no'], data['p4_contact'], data['p5_name'], data['p5_ign'], data['p5_game_id'], data['p5_id_no'], data['p5_contact']))
            conn.commit()

            del email_tokens[emails]
            return 'Authentication successful. You are now registered for VALORANT in gameathon.'
        except mysql.connector.Error as err:
            print("Error inserting data:", err)
            conn.rollback()
            return jsonify({'message': 'Error inserting data into database.'}), 500
    else:
        return jsonify({'message': 'Invalid or expired verification link.'}), 400
