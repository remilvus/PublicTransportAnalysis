import ftplib
import os
import time
from datetime import date, datetime

# names of all GTFS files that are to be archived
filenames = {'GTFS_KRK_T.zip', 'VehiclePositions_T.pb', 'TripUpdates_T.pb', 'TripUpdates_A.pb', 'GTFS_KRK_A.zip', 'ServiceAlerts_T.pb', 'ServiceAlerts_A.pb', 'VehiclePositions_A.pb'}

#  time of last download
last_pull = {name: -1 for name in filenames}


def save(ftp: ftplib.FTP, filename: str, save_as: str):
    if last_pull[filename] == save_as:
        return

    # check/prepare data folder
    folder, ext = filename.split('.')
    if not os.path.exists('data'):
        os.mkdir('data')
    path = fr'data/{folder}'
    if not os.path.exists(path):
        os.mkdir(path)

    # make local copy of the file
    with open(fr'{path}/{save_as}.{ext}', 'wb') as f:
        ftp.retrbinary(f'RETR {filename}', f.write)
        last_pull[filename] = save_as


def main():
    while True:
        try:
            ftp = ftplib.FTP('ztp.krakow.pl')
            ftp.login()
            ftp.cwd('pliki-gtfs')
            while True:
                try:
                    for filename, file_info in ftp.mlsd():
                        if filename not in filenames:
                            continue
                        save(ftp, filename, file_info['modify'])
                    time.sleep(25)
                except ftplib.error_temp:
                    print(f'{datetime.now()}\ttimeout')
                    break
        except Exception as err:
            with open('error_log.txt', 'a') as f:
                f.write(f'{datetime.now()}\t|\t{err}\n\n')


if __name__ == '__main__':
    main()
