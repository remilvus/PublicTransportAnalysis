import json

from processing.proto_processing import *
from utilities.Constants import *
from managers.StatManager import StatManager
from managers.TableManager import TableManager
from processing import result_calculation

#import visualization


if __name__ == "__main__":
    bus_informant_path = f'{DATA_PATH}/{BUS_INFO_FOLDER}'
    tram_informant_path = f'{DATA_PATH}/{TRAM_INFO_FOLDER}'
    bus_positions_path = f'{DATA_PATH}/{BUS_POSITIONS_PATH}'
    tram_positions_path = f'{DATA_PATH}/{TRAM_POSITIONS_PATH}'

    #  bus processing
    bus_stat_tracker = StatManager()

    informant = TableManager(bus_informant_path)
    vehicle_delays, arrivals = process_positions(bus_positions_path, informant, bus_stat_tracker)
    stop2location = informant.get_stop2location()

    bus_stat_tracker.summarise("Buses")

    #  tram processing
    tram_stat_tracker = StatManager()

    informant = TableManager(tram_informant_path)
    tram_delays, tram_arrivals = process_positions(tram_positions_path, informant, tram_stat_tracker)
    vehicle_delays.update(tram_delays)
    arrivals.update(tram_arrivals)
    stop2location.update(informant.get_stop2location())

    tram_stat_tracker.summarise("Trams")

    with open("arrivals.json", "w") as f:
        f.write(json.dumps(arrivals))

    # todo: assign shorter names to every stop

    data_package = dict()
    data_package["vehicle_delays"] = result_calculation.process_delays(vehicle_delays)
    data_package["recovered_schedule"] = result_calculation.calculate_schedule(arrivals)
    data_package["stop2location"] = stop2location
    # data_package["stop2name"] =

    with open("data_package.json", "w") as f:
        json.dump(data_package, f)

    # visualization.make_map(stop2location, filtered_data)
    #
    # visualization.hist(filtered_data)
