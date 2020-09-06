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

    visualization.make_map(stop2location, delays)

    visualization.hist(delays)
