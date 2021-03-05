from ftplib import FTP
import time
from datetime import datetime
from io import BytesIO

# names of all GTFS files that are to be archived
filenames = ['GTFS_KRK_T.zip', 'VehiclePositions_T.pb', 'TripUpdates_T.pb',
             'TripUpdates_A.pb', 'GTFS_KRK_A.zip',
             'ServiceAlerts_T.pb', 'ServiceAlerts_A.pb',
             'VehiclePositions_A.pb']
# saved properties
file_properties = ['size', 'modify', 'create']
time_format = '%d/%m/%Y %H:%M:%S'

# binary of last file
last_file_bin = {name: -1 for name in filenames}
# file info of last file
last_file_info = {name: -1 for name in filenames}
# file logs
file_log = {name: -1 for name in filenames}
# error log
err_log = -1
# ftp object
ftp = -1


# mlsd returns time as string
def get_time(c):
    return datetime(int(c[0:4]), int(c[4:6]), int(c[6:8]),
                    int(c[8:10]), int(c[10:12]), int(c[12:14])).strftime(
        time_format)


# returns ftp object
def get_ftp():
    ret = FTP('ztp.krakow.pl')
    ret.login()
    ret.cwd('pliki-gtfs')
    return ret


# process single file
def process_file(name, file_info):
    # we don't need full info returned by mlsd
    needed_info = {fp: file_info[fp] for fp in file_properties}

    # download file
    with BytesIO() as b:
        ftp.retrbinary(f'RETR {name}', b.write)
        file_content = b.getvalue()

    # test if metadata has changed
    info_was_changed = not last_file_info[name] == needed_info
    if info_was_changed:
        last_file_info[name] = needed_info

    # test if binary has changed
    file_was_changed = not last_file_bin[name] == file_content
    if file_was_changed:
        last_file_bin[name] = file_content

    # log
    if (info_was_changed or file_was_changed) and not skip_entry:
        print(datetime.now().strftime(time_format), get_time(info['modify']),
              get_time(info['create']),
              info['size'], info_was_changed, file_was_changed, sep=',',
              file=file_log[name], flush=True)


if __name__ == '__main__':
    # login
    ftp = get_ftp()

    try:
        err_log = open('error_log.txt', 'a')
        for name in filenames:
            file_log[name] = open(name + '.csv', 'x')
            print(
                'Log time,Modify time,Create time,Size,Metadata changed,Binary changed',
                file=file_log[name], flush=True)
    except Exception as err:
        print(err)
        print(f'{datetime.now().strftime(time_format)}\t|\t{err}', file=err_log,
              flush=True)
        quit()

    # skip the first log
    skip_entry = True

    while True:
        try:
            for name, info in ftp.mlsd():
                if name in filenames:
                    process_file(name, info)
        except Exception as err:
            print(err)
            print(f'{datetime.now().strftime(time_format)}\t|\t{err}',
                  file=err_log, flush=True)
            ftp = get_ftp()
        skip_entry = False
        time.sleep(25)
