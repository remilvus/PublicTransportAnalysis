from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from tqdm import tqdm
from Constants import PLOT_TIME_STEP, SEC_IN_DAY


# time formatting

def fix_time(t):
    """
    :param t: time of day in seconds
    :return: `t` in interval [0, 24*60*60)
    """
    return t % SEC_IN_DAY


def round_time(t, resolution=PLOT_TIME_STEP):
    """
    :param t: time of day in seconds
    :param resolution: specifies resolution of returned value (in seconds)
    :return: time (in seconds) rounded to the nearest half-hour
    """
    return int(round(t / resolution)) * resolution


def human_time(t):
    """
    :param t: time of day in seconds
    :return: time in human-readable format
    """
    hour = t // 3600
    minute = int(t / 60) % 60
    if hour < 10:
        hour = f"0{hour}"
    if minute < 10:
        minute = f"0{minute}"
    return f"{hour}:{minute}"


# statistics calculation
def append_delay_stats(collector, t, delays):
    collector["x"].append(t / 3600)
    collector["labels"].append(human_time(fix_time(t)))
    collector["y"].append(np.mean(delays) / 60)
    collector["std"].append(np.std(delays) / 60)
    

def calculate_general_stats(delays):
    accumulated_delays = defaultdict(lambda: [])

    # group
    for stop_delays in delays:
        for planned_time, trip_delays in stop_delays.items():
            t = round_time(fix_time(planned_time))
            accumulated_delays[t] += trip_delays

    # calculate statistics
    general_stats = defaultdict(lambda: [])
    for h, real in accumulated_delays.items():
        append_delay_stats(general_stats, h, real)

    return general_stats


def calculate_route_stats(delays):
    route_stats = defaultdict(lambda: {"x": [], "y": [], "std": [], "labels": []})

    for route, stop_delays in delays:
        # todo: accumulate delays when there is a small number of them
        for planned_time, delays in stop_delays.items():
            append_delay_stats(route_stats[route], planned_time, delays)

    return route_stats


def stats2html_plot(delay_info, classname, title, display='block'):
    fig = px.scatter(delay_info, x="x", y="y", error_y="std",
                     hover_name=delay_info["labels"], title=title, hover_data={'x': False, 'y': ':.0f',
                                                                               'std': ':.2f'})
    fig.update_layout(font={'size': 25})
    html = fig.to_html(include_plotlyjs=False, full_html=False)
    return f"\n<div class='delay_plot {classname}' style='display:{display};'>" + html + "</div>\n"


def make_map(stops, accumulated_delays):
    krk = folium.Map(location=[50.083795, 19.926412])

    cluster = MarkerCluster()

    # load html with js function to show/hide plots
    with open("plot_toggle.html") as f:
        plot_toggle = f.read()

    progress_bar = tqdm(list(stops.items())[:100])
    ignored_stops = 0
    for stop, location in progress_bar:
        general_stats = calculate_general_stats(accumulated_delays[stop].values())
        route_stats = calculate_route_stats(accumulated_delays[stop].items())

        if len(general_stats["x"]) <= 4:
            ignored_stops += 1
            progress_bar.set_description(f"ignored_stops = {ignored_stops}")
            continue

        html_plots = dict()

        html_plots['all_routes'] = stats2html_plot(general_stats, f"{stop}_all_routes", title=f'all delays',
                                                   display='block')

        for route, delays in route_stats.items():
            html_plots[route] = stats2html_plot(delays, f"{stop}_{route}", title=f'delays {route}')

        select = [plot_toggle, '<select name="cars" id="cars">']
        for route, html in html_plots.items():
            select.append(f'<option onclick="plot_toggle(\'{stop}\', \'{route}\');">{route}</option>\n')

        select.append("</select>\n")
        select = "".join(select)

        iframe = folium.IFrame(select + "".join(html_plots.values()), height="700px", width='900px')
        popup = folium.Popup(iframe, parse_html=False)

        marker = folium.Marker(location=location, tooltip=stop, popup=popup)
        cluster.add_child(marker)

    krk.add_child(cluster)
    krk.add_child(folium.plugins.Fullscreen())

    krk.save('krk_map.html')


def hist(delays):
    x = []
    for route, bus_bus_delays in delays.items():
        for stop, d in bus_bus_delays.items():
            for delay, count in d.items():
                x += count

    plt.figure(figsize=(8, 8), facecolor='w')
    plt.yscale('log')
    plt.hist(list(map(lambda q: q // 60, x)), bins=50)
    plt.show()
