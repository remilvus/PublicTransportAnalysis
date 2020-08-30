def pb2datetime(filename):
    current_date = datetime.datetime.strptime(filename, '%Y%m%d%H%M%S.pb')
    return current_date


def process_entity(entity, informant, trips, delays):
    stop_id = entity.vehicle.stop_id
    timestamp = entity.vehicle.timestamp
    license_plate = entity.vehicle.vehicle.license_plate

    if license_plate in trips:
        info = trips[license_plate]
        trip_id = entity.vehicle.trip.trip_id
        try:
            route = informant.trip2route(trip_id)
        except KeyError:
            route = ""

        if not info.is_correct(route):
            trips[license_plate].save_delays(delays)
            try:
                info = TripManager(entity, informant)
            except KeyError:
                return timestamp
            trips[license_plate] = info
        else:
            info.update(stop_id, timestamp, entity)
    else:
        try:
            info = TripManager(entity, informant)
        except KeyError:
            return timestamp

        trips[license_plate] = info

    return timestamp


def process_positions(postitons_path, informant):
    trips = dict()
    delays = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))

    feed = gtfs_realtime_pb2.FeedMessage()

    trips_deleted = 0
    iterator = tqdm(sorted(os.listdir(postitons_path)), position=0)
    for i, filename in enumerate(iterator):
        current_date = pb2datetime(filename)
        iterator.set_description(f'{current_date} | inactive={trips_deleted}')
        informant.update(current_date)

        with open(f'{postitons_path}/{filename}', "rb") as f:
            try:
                feed.ParseFromString(f.read())
            except Exception as err:
                if str(err) != 'Error parsing message':
                    print(err)
                continue

        timestamp = 0
        for entity in feed.entity:
            timestamp = max(process_entity(entity, informant, trips, delays), timestamp)

        if i % 10 == 0 and timestamp != 0:
            inactive = set()
            for k, v in trips.items():
                if not v.is_alive(timestamp):
                    inactive.add(k)

            trips_deleted = len(inactive)

            for license_plate in inactive:
                trips[license_plate].save_delays(delays)
                trips.pop(license_plate)

    for k, v in trips.items():
        v.save_delays(delays)

    return delays