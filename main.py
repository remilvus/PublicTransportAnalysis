from google.transit import gtfs_realtime_pb2
from collections import defaultdict
from tqdm import tqdm
from TableManager import TableManager
from TripManager import TripManager
import os
import datetime
from Constants import DATA_PATH, BUS_INFO_FOLDER, TRAM_INFO_FOLDER
import matplotlib.pyplot as plt
from mapper import visualise


bus_info_path = f'{DATA_PATH}/{BUS_INFO_FOLDER}'
trips = dict()
bus_info = TableManager(bus_info_path)
delays = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
feed = gtfs_realtime_pb2.FeedMessage()


def pb2datetime(filename):
    current_date = datetime.datetime.strptime(filename, '%Y%m%d%H%M%S.pb')
    return current_date


iterator = tqdm(sorted(os.listdir('./data/VehiclePositions_A/')), position=0)
for i, filename in enumerate(iterator):
    current_date = pb2datetime(filename)
    iterator.set_description(f'{current_date}')
    bus_info.update(current_date)
    with open(f'./data/VehiclePositions_A/{filename}', "rb") as f:
        try:
            feed.ParseFromString(f.read())
        except Exception as err:
            if str(err) != 'Error parsing message':
                print(err)
            continue

    for entity in feed.entity:
        stop_id = entity.vehicle.stop_id
        license_plate = entity.vehicle.vehicle.license_plate
        timestamp = entity.vehicle.timestamp

        if license_plate in trips:
            info = trips[license_plate]
            trip_id = entity.vehicle.trip.trip_id
            try:
                if info.route != bus_info.trip2route(trip_id):
                    trips[license_plate].save_delays(delays)
                    route = bus_info.trip2route(trip_id)
                    stop_info = bus_info.route2stop_info(route)
                    info = TripManager(entity, stop_info, route)
                    trips[license_plate] = info
                else:
                    info.update(stop_id, timestamp, entity)
            except KeyError:
                continue
        else:
            trip_id = entity.vehicle.trip.trip_id
            try:
                route = bus_info.trip2route(trip_id)
            except KeyError:
                continue
            stop_info = bus_info.route2stop_info(route)
            info = TripManager(entity, stop_info, route)
            trips[license_plate] = info

    if i % 10 == 0 and timestamp != 0:
        bad = set()
        for k, v in trips.items():
            if not info.is_alive(timestamp):
                bad.add(k)
        for ded in bad:
            trips[ded].save_delays(delays)
            trips.remove(ded)

visualise(bus_info.current_info["stop2loc"], delays)

x = []
for route, bus_delays in delays.items():
    for stop, d in bus_delays.items():
        for delay, count in d.items():
            x += count

plt.figure(figsize=(8, 8), facecolor='w')
plt.yscale('log')
plt.hist(list(map(lambda q: q//60, x)), bins=50)
plt.show()
