import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

from utilities.constants import AUTH_FOLDER, GDRIVE_DATA_PATH

MIME_FOLDER = 'application/vnd.google-apps.folder'
TOKEN_PATH = AUTH_FOLDER.joinpath('token')
CRED_PATH = AUTH_FOLDER.joinpath('credentials.json')


class Drive():
    def __init__(self):
        credentials = self._get_credentials()
        service = build('drive', 'v3', credentials=credentials)
        self.drive_client = service.files()

    @staticmethod
    def _get_credentials():
        # If modifying these scopes, delete the file token.pickle.
        scopes = [
            'https://www.googleapis.com/auth/drive']  # 'https://www.googleapis.com/auth/drive.metadata.readonly',

        credentials = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if TOKEN_PATH.exists():
            with TOKEN_PATH.open(mode='rb') as token:
                credentials = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CRED_PATH, scopes)
                except FileNotFoundError:
                    if not AUTH_FOLDER.exists():
                        AUTH_FOLDER.mkdir() # CREDENTIALS MUST BE HERE
                    raise FileNotFoundError(
                        "No crecentials found. Help: https://developers.google.com/drive/api/v3/quickstart/python#step_3_set_up_the_sample")
                credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(credentials, token)

        return credentials

    def _create_folder(self, name, parents=[]):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parents:
            file_metadata['parents'] = parents
        file = self.drive_client.create(body=file_metadata,
                                        fields='id').execute()
        return file

    def get_folder(self, folder_name):
        main_result = self.drive_client.list(
            q=f"mimeType='{MIME_FOLDER}' and name='{GDRIVE_DATA_PATH}'",
            fields='files/id, files/parents, files/name').execute()
        parend_id = None  # for id of parent folder
        if len(main_result['files']) == 0:
            file = self._create_folder(GDRIVE_DATA_PATH)
            parend_id = file['id']
        else:
            assert len(main_result[
                           'files']) == 1, f'only one folder on the drive should be named {GDRIVE_DATA_PATH}'
            parend_id = main_result['files'][0]['id']

        result = self.drive_client.list(
            q=f"mimeType='{MIME_FOLDER}' and name='{folder_name}' and '{parend_id}' in parents",
            fields='files/id, files/parents, files/name').execute()

        if len(result['files']) == 0:
            file = self._create_folder(folder_name, parents=[parend_id])
            return file['id']
        else:
            assert len(result['files']) == 1
            return result['files'][0]['id']

    def save_to_drive(self, file_path, filename, folder_name):
        folder_id = self.get_folder(self.drive_client, folder_name)
        # prepare file body
        media_body = MediaFileUpload(filename=file_path, resumable=True)

        # construct upload kwargs
        create_kwargs = {
            'body': {
                'name': filename,
                'parents': [folder_id]
            },
            'media_body': media_body,
            'fields': 'id',
        }

        # send create request
        self.drive_client.create(**create_kwargs).execute()
