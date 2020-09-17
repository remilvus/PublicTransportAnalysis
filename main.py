import json

from proto_processing import *
from Constants import *
from StatManager import StatManager
from TableManager import TableManager
import visualization


if __name__ == "__main__":
    bus_informant_path = f'{DATA_PATH}/{BUS_INFO_FOLDER}'
    tram_informant_path = f'{DATA_PATH}/{TRAM_INFO_FOLDER}'
    bus_positions_path = f'{DATA_PATH}/{BUS_POSITIONS_PATH}'
    tram_positions_path = f'{DATA_PATH}/{BUS_POSITIONS_PATH}'

    #  bus processing
    bus_stat_tracker = StatManager()

    informant = TableManager(bus_informant_path)
    delays = process_positions(bus_positions_path, informant, bus_stat_tracker)
    stop2location = informant.get_stop2location()

    bus_stat_tracker.summarise("Buses")

    #  tram processing

    tram_stat_tracker = StatManager()

    informant = TableManager(tram_informant_path)
    delays.update(process_positions(tram_positions_path, informant, tram_stat_tracker))
    stop2location.update(informant.get_stop2location())

    tram_stat_tracker.summarise("Trams")

    filtered_data = dict(dict(dict(dict())))
    for mode, mode_data in delays.items():
        filtered_data[mode] = dict()
        for stop, stop_data in mode_data.items():
            filtered_data[mode][stop] = dict()
            for line, line_data in stop_data.items():
                filtered_data[mode][stop][line] = dict()
                for planned, dels in line_data.items():
                    vehicle_delays = delays[mode][stop][line][planned]
                    if len(vehicle_delays) > 2:
                        filtered_data[mode][stop][line][planned] = vehicle_delays

    with open("delay_info.json", "w") as f:
        f.write(json.dumps(filtered_data))

    with open("stop2location.json", "w") as f:
        json.dump(stop2location, f)
    visualization.make_map(stop2location, filtered_data)

    visualization.hist(filtered_data)
