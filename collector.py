import os
import time
import ftplib
import pickle
from datetime import datetime
from io import BytesIO

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# names of all GTFS files that are to be archived
filenames = {'GTFS_KRK_T.zip', 'VehiclePositions_T.pb', 'TripUpdates_T.pb', 'TripUpdates_A.pb', 'GTFS_KRK_A.zip',
             'ServiceAlerts_T.pb', 'ServiceAlerts_A.pb', 'VehiclePositions_A.pb'}

#  time of last download
last_pull = {name: -1 for name in filenames}
#  contents of last file
last_file = {name: None for name in filenames}

DATA_PATH = 'data'
MIME_FOLDER = 'application/vnd.google-apps.folder'


#  google drive management
def get_credentials():
    # If modifying these scopes, delete the file token.pickle.
    scopes = ['https://www.googleapis.com/auth/drive']  # 'https://www.googleapis.com/auth/drive.metadata.readonly',

    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return credentials


#  google drive management
def get_folder(drive_client, name):
    main_result = drive_client.list(q=f"mimeType='{MIME_FOLDER}' and name='{DATA_PATH}'",
                                    fields='files/id, files/parents, files/name').execute()
    parend_id = None  # for id of parent folder
    if len(main_result['files']) == 0:
        file_metadata = {
            'name': DATA_PATH,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = drive_client.create(body=file_metadata,
                                   fields='id').execute()
        parend_id = file['id']
    else:
        assert len(main_result['files']) == 1
        parend_id = main_result['files'][0]['id']

    result = drive_client.list(q=f"mimeType='{MIME_FOLDER}' and name='{name}' and '{parend_id}' in parents",
                               fields='files/id, files/parents, files/name').execute()

    if len(result['files']) == 0:
        file_metadata = {
            'name': name,
            'parents': [parend_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = drive_client.create(body=file_metadata,
                                   fields='id').execute()
        return file['id']
    else:
        assert len(result['files']) == 1
        return result['files'][0]['id']


#  google drive management
def save_to_drive(drive_client, file_path, filename, folder_name):
    folder_id = get_folder(drive_client, folder_name)
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
    drive_client.create(**create_kwargs).execute()


def save_file(ftp: ftplib.FTP, filename: str, save_as: str, drive_client=None, delete_local=False):
    assert not (drive_client is None and delete_local), "files won't be saved"

    if last_pull[filename] == save_as:
        return

    # prepare folder/file names
    folder, ext = filename.split('.')
    local_filename = f'{save_as}.{ext}'
    directory = os.path.join('data', folder)

    # check/prepare data folder
    if not os.path.exists('data'):
        os.mkdir('data')
    if not os.path.exists(directory):
        os.mkdir(directory)

    # retrieve file
    with BytesIO() as b:
        ftp.retrbinary(f'RETR {filename}', b.write)
        file_content = b.getvalue()

    # check whether the file has changed since last pull
    if last_file[filename] == file_content:
        return

    # make local copy of the file
    with open(fr'{directory}/{save_as}.{ext}', 'wb') as f:
        f.write(file_content)

    file_path = os.path.join(directory, local_filename)
    if drive_client is not None:
        save_to_drive(drive_client, file_path, local_filename, folder)

    last_pull[filename] = save_as
    last_file[filename] = file_content

    if delete_local:
        os.remove(file_path)


def main():
    while True:
        try:
            ftp = ftplib.FTP('ztp.krakow.pl')
            ftp.login()
            ftp.cwd('pliki-gtfs')

            credentials = get_credentials()
            service = build('drive', 'v3', credentials=credentials)
            # get drive client
            drive_client = service.files()
            timestamp = time.time()
            while True:
                try:
                    for filename, file_info in ftp.mlsd():
                        if filename not in filenames:
                            continue
                        save_file(ftp, filename, file_info['modify'], drive_client, delete_local=True)

                    sleep_time = 25 + timestamp - time.time()
                    if sleep_time < 0:
                        sleep_time = 0
                    time.sleep(sleep_time)
                    timestamp = time.time()
                except ftplib.error_temp:
                    print(f'{datetime.now()}\ttimeout')
                    break
        except Exception as err:
            with open('error_log.txt', 'a') as f:
                f.write(f'{datetime.now()}\t|\t{repr(err)}\n\n')


if __name__ == '__main__':
    main()
