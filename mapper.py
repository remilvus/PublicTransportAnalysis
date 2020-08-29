import folium
from folium.plugins import MarkerCluster
from tqdm import tqdm
import plotly.express as px
import numpy as np


def visualise(stops, delays):
    krk = folium.Map(location=[50.083795, 19.926412])

    cluster = MarkerCluster()
    for stop, location in tqdm(stops.items()):
        x = []
        std = []
        y = []
        all_times = {i: [] for i in range(0, 60*24, 30)}
        for route, d in delays[stop].items():
            for planned_time, dex in d.items():
                all_times[(int(round(planned_time / 3600) * 60)) % (24 * 60)] += dex

        for tim, dels in all_times.items():
            if len(dels) > 5:
                x.append(tim)
                dels = list(map(lambda q: q // 60, dels))
                std.append(np.std(dels))
                y.append(np.mean(dels))

        if len(x) < 5:
            continue

        fig = px.scatter(x=list(map(lambda q: q // 60, x)), y=y, error_y=std, title='delays')
        html = fig.to_html(include_plotlyjs='cdn')

        iframe = folium.IFrame(html, width=632 + 20, height=420 + 20)
        popup = folium.Popup(iframe, parse_html=True)

        marker = folium.Marker(location=location, tooltip=stop, popup=popup)
        cluster.add_child(marker)

    krk.add_child(cluster)
    krk.add_child(folium.plugins.Fullscreen())
    krk.save('krk_map.html')
