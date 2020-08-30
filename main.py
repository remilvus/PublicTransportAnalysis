from TableManager import TableManager
from Constants import *
import matplotlib.pyplot as plt
from mapper import visualise
from proto_processing import *


if __name__ == "__main__":
    bus_informant_path = f'{DATA_PATH}/{BUS_INFO_FOLDER}'
    tram_informant_path = f'{DATA_PATH}/{TRAM_INFO_FOLDER}'
    bus_positions_path = f'{DATA_PATH}/{BUS_POSITIONS_PATH}'
    tram_positions_path = f'{DATA_PATH}/{BUS_POSITIONS_PATH}'


    informant = TableManager(bus_informant_path)
    delays = process_positions(bus_positions_path, informant)
    stop2loc = informant.current_info["stop2loc"]

    informant = TableManager(tram_informant_path)
    delays.update(process_positions(tram_positions_path, informant))
    stop2loc.update(informant.current_info["stop2loc"])

    visualise(stop2loc, delays)

    x = []
    for route, bus_bus_delays in delays.items():
        for stop, d in bus_bus_delays.items():
            for delay, count in d.items():
                x += count

    plt.figure(figsize=(8, 8), facecolor='w')
    plt.yscale('log')
    plt.hist(list(map(lambda q: q//60, x)), bins=50)
    plt.show()
