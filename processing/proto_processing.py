import datetime
import os
from collections import defaultdict

from tqdm import tqdm
from google.transit import gtfs_realtime_pb2

from managers.TripManager import TripManager
from utilities import gtfs_extraction as ext


def pb2datetime(filename):
    current_date = datetime.datetime.strptime(filename, '%Y%m%d%H%M%S.pb')
    return current_date


def process_entity(entity, informant, trips, delays, arrivals, stat_tracker=None):
    timestamp = ext.get_epoch_time(entity)
    license_plate = ext.get_license_plate(entity)

    if license_plate in trips:
        info = trips[license_plate]
        info.update(entity)
    else:
        info = TripManager(entity, informant, delays, arrivals, stat_tracker)
        trips[license_plate] = info

    return timestamp


def process_positions(positions_path, informant, stat_tracker=None):
    trips = dict()
    delays = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: []))))
    arrivals = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))

    feed = gtfs_realtime_pb2.FeedMessage()

    trips_deleted = 0
    iterator = tqdm(sorted(os.listdir(positions_path)), position=0)
    for i, filename in enumerate(iterator):
        current_date = pb2datetime(filename)
        table_name = informant.update(current_date)

        iterator.set_description(f'{table_name} | {current_date} | inactive={trips_deleted}')

        with open(f'{positions_path}/{filename}', "rb") as f:
            try:
                feed.ParseFromString(f.read())
            except Exception as err:
                if str(err) != 'Error parsing message':
                    print(err)
                continue

        timestamp = 0
        for entity in feed.entity:
            timestamp = max(process_entity(entity, informant, trips, delays, arrivals, stat_tracker), timestamp)

        if i % 10 == 0 and timestamp != 0:
            inactive = set()
            for k, v in trips.items():
                if not v.is_alive(timestamp):
                    inactive.add(k)

            trips_deleted = len(inactive)

            for license_plate in inactive:
                trips[license_plate].save_delays()
                trips.pop(license_plate)

    for k, v in trips.items():
        v.save_delays()

    return delays, arrivals