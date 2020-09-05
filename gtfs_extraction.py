
# short functions for extracting information from VehiclePosition entities


def get_trip_id(entity):
    return entity.vehicle.trip.trip_id


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
