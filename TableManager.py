import datetime
import os
from collections import defaultdict
import pandas as pd
from zipfile import ZipFile
from Constants import SEC_IN_DAY

class TableManager:
    def __init__(self, bus_data_path):
        self.bus_data_path = bus_data_path
        self.bus_files = sorted([{"date": datetime.datetime.strptime(f, '%Y%m%d%H%M%S.zip'),
                                  "filename": f} for f in os.listdir(bus_data_path)], key=lambda x: x["date"])
        self.current_file = 0
        self.current_tables = self.load_tables(self.bus_files[0]["filename"])
        self.current_info = self.extract_info(self.current_tables)
        self.previous_tables = dict()
        self.previous_info = defaultdict(lambda: set())

    def update(self, date):
        if self.current_file + 1 < len(self.bus_files) and \
                self.bus_files[self.current_file + 1]["date"] < date:
            print(date)
            self.current_file += 1
            self.previous_tables = self.current_tables
            self.current_tables = self.load_tables(self.bus_files[self.current_file]["filename"])
            self.previous_info = self.current_info
            self.current_info = self.extract_info(self.current_tables)

    def stop2routes(self, stop):
        return self.current_info["stop2routes"][stop] | self.previous_info["stop2routes"][stop]

    def trip2route(self, trip):
        return self.current_info["trip2route"][trip]

    def route2stops(self, route):
        return self.current_info["route2stops"][route]

    def route2stop_info(self, route):
        return self.current_info["route2stop_info"][route]

    def load_tables(self, filename):
        tables = dict()
        with ZipFile(f'{self.bus_data_path}/{filename}', 'r') as zipObj:
            for name in zipObj.namelist():
                tables[name.split('.')[0]] = pd.read_csv(zipObj.open(name))
        return tables

    @staticmethod
    def get_routes(df: pd.DataFrame):
        df = df.set_index('route_id')
        return {k: v['route_short_name'] for k, v in df[['route_short_name']].to_dict('index').items()}

    @staticmethod
    def get_trip2route(df: pd.DataFrame):
        df = df.set_index('trip_id')
        return {k: v['route_id'] for k, v in df[['route_id']].to_dict('index').items()}

    @staticmethod
    def get_stop2loc(df: pd.DataFrame):
        df = df.set_index('stop_id')
        return {k: (v['stop_lat'], v['stop_lon']) for k, v in df[['stop_lat', 'stop_lon']].to_dict('index').items()}

    @staticmethod
    def get_route2stop_info(trip2route, stop_df: pd.DataFrame):
        stop_df["route"] = stop_df.trip_id.map(lambda x: trip2route[x])
        
        def make_stop2time(df):
            stop2time = defaultdict(lambda: set())
            for s, t in zip(df['stop_id'], df['arrival_time']):
                stop2time[s].add((int(t[0:2]) * 60 * 60 + int(t[3:5]) * 60) % SEC_IN_DAY)  # in seconds since midnight
            return stop2time

        route2stop_info_df = stop_df[['stop_id', 'route', 'arrival_time']].groupby('route'). \
            apply(lambda x: make_stop2time(x))

        return route2stop_info_df.to_dict()

    @staticmethod
    def get_stop2routes(trip2route, stop_df: pd.DataFrame):
        stop2trips_df = stop_df[['stop_id', 'trip_id']].groupby('stop_id').apply(lambda x: x.trip_id.tolist())
        stop2routes = defaultdict(lambda: set())
        for k, v in stop2trips_df.to_dict().items():
            stop2routes[k] |= {trip2route[trip] for trip in v}
        return stop2routes

    @staticmethod
    def extract_info(tables):
        trip2route = TableManager.get_trip2route(tables['trips'])
        return {"routes": TableManager.get_routes(tables['routes']),
                "stop2loc": TableManager.get_stop2loc(tables['stops']),
                "trip2route": trip2route,
                "stop2routes": TableManager.get_stop2routes(trip2route, tables['stop_times']),
                "route2stop_info": TableManager.get_route2stop_info(trip2route, tables['stop_times'])
                }
