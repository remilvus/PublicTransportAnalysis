from collections import defaultdict
from Constants import SEC_IN_DAY


class TripManager:
    def __init__(self, entity, stop_time, route):        
        self.route = route
        self.license_plate = entity.vehicle.vehicle.license_plate
        self.stop_time = stop_time
        self.delays = defaultdict(lambda: defaultdict(lambda: []))
        self.last_epoch = entity.vehicle.timestamp
        self.next_stop = entity.vehicle.stop_id
        self.update_limit = 60 * 60 # time in s without update
        self.inconsistent = False

    def update(self, stop_id, epoch_time, entity=None):
        if epoch_time != 0:
            if len(self.stop_time[stop_id]) == 0:
                self.inconsistent = True

            if stop_id != self.next_stop and len(self.stop_time[stop_id]) != 0:  # calculate_delay
                self.next_stop = stop_id
                arrival_time = epoch_time + 2 * 60 * 60  # time zone correction
                arrival_time = arrival_time % (24 * 60 * 60)
                diff = map(lambda plan: (arrival_time - plan, plan), self.stop_time[stop_id])

                diff = map(lambda t: t if abs(t[0]) < SEC_IN_DAY // 2 else (self.fix_diff(t[0]), t[1]), diff)

                best_fit = sorted(diff, key=lambda x: x[0] if x[0] >= 0 else 3*abs(x[0]))[0]

                self.delays[stop_id][best_fit[1]].append(best_fit[0])

            self.last_epoch = epoch_time

    @staticmethod
    def fix_diff(seconds):
        if seconds > 0:
            return seconds - SEC_IN_DAY
        return seconds + SEC_IN_DAY

    def save_delays(self, acc):
        if self.inconsistent:
            return

        for stop, delays in self.delays.items():
            for time, count in delays.items():
                acc[stop][self.route][time] = acc[stop][self.route][time] + count

    def is_alive(self, time):
        return (time - self.last_epoch) < self.update_limit
