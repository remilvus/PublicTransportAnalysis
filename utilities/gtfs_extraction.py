# utilities for extracting and managing information from gtfs entities
import pathlib

from google.transit import gtfs_realtime_pb2


class VehiclePosition:
    def __init__(self, filepath: pathlib.Path):
        feed = gtfs_realtime_pb2.FeedMessage()

        with filepath.open(mode='rb') as f:
            try:
                feed.ParseFromString(f.read())
            except Exception as err:
                if str(err) != 'Error parsing message':
                    print(err)

        self.gtfs_version = feed.header.gtfs_realtime_version
        self.header_timestamp = feed.header.timestamp

        entity = feed.entity
        # todo: extract information from entity
        print("\n\n\nEntity: ", feed.entity)


class TripUpdates:
    pass


class ServiceAlerts:
    pass



def get_trip_id(entity):
    return entity.vehicle.trip.trip_id


# old functions from prototype
def get_service(entity):
    return int(get_trip_id(entity)[-1])


def get_epoch(entity):
    return entity.vehicle.timestamp


def get_stop_id(entity):
    return entity.vehicle.stop_id


def get_license_plate(entity):
    return entity.vehicle.vehicle.license_plate


def get_epoch_time(entity):
    return entity.vehicle.timestamp


def get_stop_status(entity):
    return entity.vehicle.current_status


if __name__=="__main__":
    from utilities.constants import VEHICLE_POSITIONS_A_PATH

    example_pb = next(VEHICLE_POSITIONS_A_PATH.iterdir())
    example_vp = VehiclePosition(example_pb)
    print(example_vp.gtfs_version, example_vp.header_timestamp)