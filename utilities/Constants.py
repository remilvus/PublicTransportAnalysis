DATA_PATH = 'data'
BUS_INFO_FOLDER = 'GTFS_KRK_A'
TRAM_INFO_FOLDER = 'GTFS_KRK_T'
BUS_POSITIONS_PATH = 'VehiclePositions_A'
TRAM_POSITIONS_PATH = 'VehiclePositions_T'
SEC_IN_DAY = 24 * 60 * 60
PLOT_TIME_STEP = 30 * 60  # specifies resolution of x axis for plots with general delay statistics
MIN_STOP_NUMBER = 3  # todo: set to length of shortest route
MAX_BUS_INACTIVITY = 20 * 60  # max time (in seconds) a trip can exist without any update


# gtfs-realtime VehicleStopStatus
INCOMING_AT = 0
STOPPED_AT = 1
IN_TRANSIT_TO = 2
