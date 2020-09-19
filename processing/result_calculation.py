from collections import defaultdict

import numpy as np
import hdbscan

from utilities import time_formating as time_form


# statistics calculation
def append_delay_stats(collector, t, delays):
    collector["x"].append(t / 3600)
    collector["labels"].append(time_form.human_time(time_form.fix_time(t)))
    collector["y"].append(np.mean(delays) / 60)
    collector["std"].append(np.std(delays) / 60)


def calculate_general_stats(delays):
    accumulated_delays = defaultdict(lambda: [])

    # group
    for stop_delays in delays:
        for planned_time, trip_delays in stop_delays.items():
            t = time_form.round_time(time_form.fix_time(planned_time))
            accumulated_delays[t] += trip_delays

    # calculate statistics
    general_stats = defaultdict(lambda: [])
    for h, real in accumulated_delays.items():
        append_delay_stats(general_stats, h, real)

    return general_stats


def calculate_route_stats(delays):
    route_stats = defaultdict(lambda: {"x": [], "y": [], "std": [],
                                       "labels": []})

    for route, stop_delays in delays:
        # todo: accumulate delays when there is a small number of them
        for planned_time, delays in stop_delays.items():
            append_delay_stats(route_stats[route], planned_time, delays)

    return route_stats


def calculate_schedule(arrivals):
    schedule =  defaultdict(lambda:
                            defaultdict(lambda:
                                        defaultdict(lambda:
                                                    defaultdict(lambda: []))))

    for mode, accumulated_arrivals in arrivals.items():
        for stop, stop_arrivals in accumulated_arrivals.items():
            for route, route_arrival in stop_arrivals.items():
                if len(route_arrival) < 5:
                    continue

                route_arrival = np.array(route_arrival)

                labels = hdbscan.HDBSCAN(min_cluster_size=2).fit_predict(
                    route_arrival.reshape(-1, 1))

                for lab in np.unique(labels):
                    if lab == -1: # Noise
                        continue
                    cluster = route_arrival[labels == lab]
                    schedule[mode][stop][route]["arrival"].append(int((np.median(cluster))))
                    schedule[mode][stop][route]["min"].append(int(np.min(cluster)))
                    schedule[mode][stop][route]["max"].append(int(np.max(cluster)))
    return schedule


def process_delays(filtered_data):
    processed_data = defaultdict(lambda: defaultdict(lambda: dict()))

    for mode, accumulated_delays in filtered_data.items():
        for stop, stop_delays in accumulated_delays.items():
            general_stats = calculate_general_stats(stop_delays.values())
            route_stats = calculate_route_stats(stop_delays.items())

            processed_data[mode][stop]["general"] = general_stats
            processed_data[mode][stop].update(route_stats)

    return processed_data