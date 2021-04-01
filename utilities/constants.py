from pathlib import Path

# project file structure
PROJECT_ROOT = Path(__file__).parent.parent

DATA_PATH = PROJECT_ROOT.joinpath('data')
RAW_DATA_PATH = DATA_PATH.joinpath('raw_data')
RAW_METADATA_PATH = DATA_PATH.joinpath('raw_metadata')
VEHICLE_POSITIONS_A_PATH = RAW_DATA_PATH.joinpath('VehiclePositions_A')
# todo: add paths to all subfolders of 'raw_data' folder

DATABASE_PATH = DATA_PATH.joinpath('databases')
GTFS_DB_PATH = DATABASE_PATH.joinpath('gtfs.db')
POSITIONS_DB_PATH = DATABASE_PATH.joinpath('vehicle_positions.db')
UPDATES_DB_PATH = DATABASE_PATH.joinpath('trip_updates.db')
ALERTS_DB_PATH = DATABASE_PATH.joinpath('alerts.db')

AUTH_FOLDER = PROJECT_ROOT.joinpath('auth')

# # Google drive folder
GDRIVE_DATA_PATH = 'data_gtfs'

# GTFS-related constants
GTFS_FILENAMES = {'GTFS_KRK_T.zip', 'VehiclePositions_T.pb', 'TripUpdates_T.pb',
                  'TripUpdates_A.pb', 'GTFS_KRK_A.zip', 'ServiceAlerts_T.pb',
                  'ServiceAlerts_A.pb', 'VehiclePositions_A.pb'}

# # gtfs-realtime VehicleStopStatus
INCOMING_AT = 0
STOPPED_AT = 1
IN_TRANSIT_TO = 2

# constants from prototype (potentially unneeded)
SEC_IN_DAY = 24 * 60 * 60

