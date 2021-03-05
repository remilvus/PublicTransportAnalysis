import time
import ftplib
import pathlib
import traceback
from datetime import datetime
from io import BytesIO

from utilities.constants import RAW_DATA_PATH, GTFS_FILENAMES, DATA_PATH
from utilities import gdrive

SAVE_LOCAL = True
SAVE_DRIVE = False
GREEDY = True
# if false the script should check whether the file should be downloaded
# the check should be performed based on size of the file and time of last
# download time from inside of protobuffers can also be used

# time between consequent downloads
SHORT_SLEEP = 1  # if <GREEDY>
LONG_SLEEP = 10  # if not <GREEDY>

SAVE_METADATA = False

assert SAVE_LOCAL or SAVE_DRIVE, "files aren't saved anywhere"

#  time of last download
last_pull = {name: -1 for name in GTFS_FILENAMES}
#  contents of last file
last_file = {name: None for name in GTFS_FILENAMES}

error_path = DATA_PATH.joinpath('collector_errors.txt')


def make_informative_name(source_tag, filename: str, file_info: dict):
    extension = '.' + filename.split('.')[-1]
    modify = file_info['modify']
    create = file_info['create']

    return "`".join([source_tag, modify, create]) + extension


def check_download() -> bool:  # todo
    """checks whether it makes sense to download the file. Should return false
       if the probability that the file has changed is low"""
    pass


def save_file(ftp: ftplib.FTP, filename: str, save_as: str, drive=None):
    if last_pull[filename] == save_as:
        return

    # prepare directory for file
    folder, _ = filename.split('.')
    directory: pathlib.Path = RAW_DATA_PATH.joinpath(folder)
    if not directory.exists():
        directory.mkdir()

    if not GREEDY:
        raise NotImplemented()  # todo
        check_download()

    # retrieve file
    with BytesIO() as b:
        ftp.retrbinary(f'RETR {filename}', b.write)
        file_content = b.getvalue()

    # check whether the file has changed since last pull
    if last_file[filename] == file_content:
        return

    # make local copy of the file
    with directory.joinpath(save_as).open('wb') as f:
        f.write(file_content)

    file_path = directory.joinpath(save_as)
    if drive is not None:
        assert SAVE_DRIVE
        drive.save_to_drive(file_path, save_as, folder)

    last_pull[filename] = save_as
    last_file[filename] = file_content

    if not SAVE_LOCAL:
        file_path.unlink()  # removes local file


def download_loop(drive: gdrive.Drive, ftp: ftplib.FTP, error_file):
    while True:
        timestamp = time.time()
        try:
            for filename, file_info in ftp.mlsd():
                if filename not in GTFS_FILENAMES:
                    continue
                informative_name = make_informative_name(source_tag='KRK',
                                                         filename=filename,
                                                         file_info=file_info)
                save_file(ftp, filename, informative_name, drive)
        except ftplib.error_temp as err:
            print(f'{datetime.now()}\ttimeout')
            error_file.write(
                f'{datetime.now()}`{type(err)}`{str(err)}`{repr(traceback.format_exc())}\n')
            break
        if GREEDY:
            sleep_time = SHORT_SLEEP
        else:
            sleep_time = LONG_SLEEP

        sleep_time += timestamp - time.time()
        if sleep_time < 0:
            sleep_time = 0
        time.sleep(sleep_time)


def main():
    error_file = error_path.open('a')
    error_file.write('=' * 20 + '\n')

    while True:
        try:
            ftp = ftplib.FTP('ztp.krakow.pl')
            ftp.login()
            ftp.cwd('pliki-gtfs')

            # get drive client
            drive = None
            if SAVE_DRIVE:
                drive = gdrive.Drive()

            download_loop(drive, ftp, error_file)
        except Exception as err:
            error_file.write(
                f'{datetime.now()}`{type(err)}`{str(err)}`{repr(traceback.format_exc())}\n')


if __name__ == '__main__':
    print('collector started')
    main()
