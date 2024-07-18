import os
from flask import Flask, request, jsonify, redirect, url_for, send_file
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CLIENT_SECRETS_FILE = 'client_secrets.json'

def get_gdrive_service():
    creds = None
    if 'google_token' in session:
        creds = Credentials.from_authorized_user_info(session['google_token'], SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        session['google_token'] = creds.to_json()
    return build('drive', 'v3', credentials=creds)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    service = get_gdrive_service()
    return redirect(service.auth_uri)

@app.route('/oauth_callback')
def oauth_callback():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    session['google_token'] = creds.to_json()
    return redirect(url_for('upload_form'))

@app.route('/upload')
def upload_form():
    return '''
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit">Upload</button>
        </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    service = get_gdrive_service()
    file_metadata = {'name': file.filename}
    media = MediaFileUpload(file, mimetype=file.content_type)
    gfile = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    return f'File uploaded successfully. File ID: {gfile.get("id")}'

@app.route('/files/<file_id>')
def download_file(file_id):
    service = get_gdrive_service()
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return send_file(fh, as_attachment=True, attachment_filename=file_id)

if __name__ == '__main__':
    app.run(debug=True)
