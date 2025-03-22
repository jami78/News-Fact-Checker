import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re
from googleapiclient.http import MediaFileUpload
import traceback

def get_google_services():
    creds = service_account.Credentials.from_service_account_file("fact-checker-450613-deb87d989f62.json", scopes=["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive.file"])
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds) # Drive API
    return docs_service, drive_service

def extract_folder_id(drive_link):
    match = re.search(r"drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)", drive_link)
    return match.group(1) if match else None

def upload_docx_to_drive(docx_filepath, drive_link):
    try:
        docs_service, drive_service = get_google_services()

        # Extract Folder ID
        folder_id = extract_folder_id(drive_link)
        if not folder_id:
            print("Error: Invalid Google Drive folder link.")
            return None

        # File metadata
        file_metadata = {
            "name": os.path.basename(docx_filepath),
            "parents": [folder_id]
        }

        # Media upload
        media = MediaFileUpload(docx_filepath, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

        # Upload the file
        try:
            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        except Exception as upload_error:
            print(f"Error during file upload: {upload_error}")
            print(traceback.format_exc())  # Print the full traceback
            return None

        # Get the file ID and webViewLink
        file_id = file.get('id')
        file_url = file.get('webViewLink')

        return file_url

    except Exception as e:
        print(f"Error uploading DOCX to Google Drive: {e}")
        print(traceback.format_exc())  # Print the full traceback
        return None
    
