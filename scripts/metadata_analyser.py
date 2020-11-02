from ftplib import FTP
import time
from datetime import datetime
from io import BytesIO

# names of all GTFS files that are to be archived
filenames = {'GTFS_KRK_T.zip', 'VehiclePositions_T.pb', 'TripUpdates_T.pb', 'TripUpdates_A.pb', 'GTFS_KRK_A.zip',
             'ServiceAlerts_T.pb', 'ServiceAlerts_A.pb', 'VehiclePositions_A.pb'}
# saved properties
file_properties = {'size', 'modify', 'create'}
time_format = '%d/%m/%Y %H:%M:%S'


# mlsd returns time as string
def get_time(c):
    return datetime(int(c[0]+c[1]+c[2]+c[3]), int(c[4]+c[5]), int(c[6]+c[7]),
                    int(c[8]+c[9]), int(c[10]+c[11]), int(c[12]+c[13])).strftime(time_format)


# binary of last file
last_file_bin = {name: {} for name in filenames}
# file info of last file
last_file_info = {name: {} for name in filenames}

if __name__ == '__main__':
    ftp = FTP('ztp.krakow.pl')
    ftp.login()
    ftp.cwd('pliki-gtfs')

    # skip the first log
    skip_entry = True

    for name in filenames:
        try:
            with open(name + '.csv', 'x') as f:
                print('Log time,Modify time,Create time,Size,File info changed,File binary changed', file=f)
        except FileExistsError as err:
            pass

    while True:
        try:
            for name, info in ftp.mlsd():
                if name not in filenames:
                    continue
                #we don't need full info returned by mlsd
                needed_info = {fp: info[fp] for fp in file_properties}

                #download file
                with BytesIO() as b:
                    ftp.retrbinary(f'RETR {name}', b.write)
                    file_content = b.getvalue()

                #test if metadata has changed
                info_was_changed = not last_file_info[name] == needed_info
                if info_was_changed:
                    last_file_info[name] = needed_info

                #test if binary has changed
                file_was_changed = not last_file_bin[name] == file_content
                if file_was_changed:
                    last_file_bin[name] = file_content

                #log
                if (info_was_changed or file_was_changed) and not skip_entry:
                    with open(name + '.csv', 'a') as f:
                        print(datetime.now().strftime(time_format), get_time(info['modify']), get_time(info['create']),
                              info['size'], info_was_changed, file_was_changed, sep=',', file=f)

        except Exception as err:
            with open('error_log.txt', 'a') as f:
                f.write(f'{datetime.now().strftime(time_format)}\t|\t{repr(err)}\n')

        skip_entry = False
        time.sleep(25)
