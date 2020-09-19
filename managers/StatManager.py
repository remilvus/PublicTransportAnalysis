
class StatManager:
    def __init__(self):
        # saving delays
        self.bad_trips = 0
        self.good_trips = 0
        self.broken_on_init = 0
        
        #  trip fixing
        self.trip_fix_requests = 0
        self.fix_result = {"fixed": 0, "failed": 0}

        #  time related
        self.bad_epoch_time = 0
        self.good_epoch_time = 0
        self.earlier_epoch = 0
        self.trip_inactive_time = 0
        self.trip_updates = 0
        
        #  other
        self.stop_status = {0: 0, 1: 0, 2: 0}
        self.data_points = 0
        self.lacking_stops = 0
        self.route_change = 0

    def summarise(self, header):
        self.draw_line()
        print(f"\n\t{header}\n")
        self.draw_line()
        if self.bad_trips > 0 or self.good_trips > 0:
            percentage = round(self.bad_trips / (self.bad_trips + self.good_trips) * 100, 1)
        else:
            percentage = 0
        
        print(f"Trips: broken = {self.bad_trips} ({percentage}%) | good = {self.good_trips}")
        print(f"Fixing result: fixed = {self.fix_result['fixed']} | failed = {self.fix_result['failed']} | total = {self.trip_fix_requests}")
        self.draw_line(15)
        print(f"Epoch time: \n\t-equaled zero {self.bad_epoch_time} times\n\t-was good {self.good_epoch_time} times")
        print(f"Epoch time got smaller {self.earlier_epoch} times")
        print(f"Mean time between trip updates = {round(self.trip_inactive_time / self.trip_updates, 2)}")
        self.draw_line(15)
        print(f"There were not enough stops to save delays {self.lacking_stops} times")
        print(f"Data points in total = {self.data_points}")
        print(f"Active trip got different route assigned {self.route_change} times")
        print(f"VehicleStopStatus at stop:\n\tincoming = {self.stop_status[0]} | stopped = {self.stop_status[1]} " +
              f"| in transit = {self.stop_status[2]}")
        self.draw_line()

    @staticmethod
    def draw_line(length=30):
        print("-" * length)
