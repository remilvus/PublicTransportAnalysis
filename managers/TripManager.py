from collections import defaultdict

from utilities.Constants import SEC_IN_DAY, MIN_STOP_NUMBER, MAX_BUS_INACTIVITY
from managers.StatManager import StatManager
from managers.TableManager import TableManager
from utilities import gtfs_extraction as ext


class TripManager:
    # initialization
    def __init__(self, entity, informant: TableManager, delay_collector, arrival_collector, stat_tracker: StatManager = None):
        self.informant = informant
        self.license_plate = ext.get_license_plate(entity)
        self.inactivity_limit = MAX_BUS_INACTIVITY
        self.stat_tracker = stat_tracker
        self.delay_collector = delay_collector
        self.arrival_collector = arrival_collector

        self._init_dynamic_info(entity)

    def _init_dynamic_info(self, entity):

        # setting flags & buffers
        self._fix_state = False
        self._broken = False
        self._delays = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
        self._arrivals = []
        self._candidate_routes = None
        self.service = ext.get_service(entity)
        # extracting information from gtfs entity & tables
        try:
            trip_id = ext.get_trip_id(entity)
            self._route = self.informant.trip2route(trip_id)
            self.short_name = self.informant.route2name(self._route)
            self.stop_time = self.informant.route2stop_info(self._route)
        except KeyError:  # trip_id not present in most recent gtfs table
            self._broken = True
            if self.stat_tracker: self.stat_tracker.broken_on_init += 1
            self._route = "no route"

        self._last_epoch = ext.get_epoch(entity)
        self._last_stop = ext.get_stop_id(entity)
        self.trip_id = trip_id

    # public methods
    def update(self, entity):
        epoch_time = ext.get_epoch(entity)
        if self._last_epoch > epoch_time:
            if self.stat_tracker: self.stat_tracker.earlier_epoch += 1
            return
        stop_id = ext.get_stop_id(entity)

        if self.stat_tracker:
            self.stat_tracker.trip_inactive_time += epoch_time - self._last_epoch
            self.stat_tracker.trip_updates += 1

        if self.trip_id != ext.get_trip_id(entity):
            self.save_delays()
            self._init_dynamic_info(entity)

        self._route_check(entity)

        if self.stat_tracker:
            if epoch_time == 0:
                self.stat_tracker.bad_epoch_time += 1
            else:
                self.stat_tracker.good_epoch_time += 1

        # todo: better epoch_time tracking (keep track of biggest seen value & manage too big changes)
        if epoch_time != 0 and not self._broken and self._stop_changed(stop_id):
            if self.stat_tracker:
                status = ext.get_stop_status(entity)
                self.stat_tracker.stop_status[status] += 1
            self._last_epoch = ext.get_epoch(entity)

            if self._fix_state:
                self._narrow_candidates(entity)
            elif len(self.stop_time[stop_id]) == 0:
                self._fix(entity)

            self._add_arrival(epoch_time)

            self._last_stop = stop_id

    def save_delays(self):
        if len(self._arrivals) < MIN_STOP_NUMBER:
            # not enough data to be sure that this trip is correct
            if self.stat_tracker: self.stat_tracker.lacking_stops += 1
            return

        if self._broken or self._fix_state:
            if self.stat_tracker: self.stat_tracker.bad_trips += 1
            return

        if self.stat_tracker: self.stat_tracker.good_trips += 1

        self._calculate_delays()
        for stop, service_delay_info in self._delays.items():
            for service, delay_info in service_delay_info.items():
                for planned_time, delays in delay_info.items():
                    self.delay_collector[service][stop][self.short_name][planned_time] += delays
                    if self.stat_tracker: self.stat_tracker.data_points += len(delays)

        for (stop, arrival) in self._arrivals:
            self.arrival_collector[self.service][stop][self.short_name].append(arrival)


    def is_alive(self, epoch_time):
        return (epoch_time - self._last_epoch) < self.inactivity_limit

    # private methods
    # # delay management
    def _add_arrival(self, epoch_time):
        arrival_time = epoch_time + 2 * 60 * 60  # time zone correction
        arrival_time = arrival_time % (24 * 60 * 60)

        self._arrivals.append((self._last_stop, arrival_time))

    def _calculate_delays(self):
        for stop_id, arrival_time in self._arrivals:
            if len(self.stop_time[stop_id]) == 0:
                self._broken = True
                return

            # calculate differences
            delay_plan = map(lambda planned_time: (arrival_time - planned_time, planned_time), self.stop_time[stop_id])
            # fix problems caused by midnight
            delay_plan = map(lambda dp: dp if abs(dp[0]) < SEC_IN_DAY // 2 else (self._fix_midnight(dp[0]), dp[1]),
                             delay_plan)
            best_fit = sorted(delay_plan, key=self._weigh_delay)[0]

            self._delays[stop_id][self.service][best_fit[1]].append(best_fit[0])

    @staticmethod
    def _fix_midnight(seconds):
        if seconds > 0:
            return seconds - SEC_IN_DAY
        return seconds + SEC_IN_DAY

    @staticmethod
    def _weigh_delay(delay_plan):
        """metric for delays. Assigns bigger values for being early"""
        delay, planned = delay_plan
        # todo: validate if it's a good way to calculate weight
        if delay >= -60 * 2:
            return delay
        else:
            return SEC_IN_DAY // 4

    # # methods related to determining the true route
    def _fix(self, entity):
        assert not self._fix_state

        if self.stat_tracker: self.stat_tracker.trip_fix_requests += 1

        stop_id = ext.get_stop_id(entity)
        stop2routes = self.informant.stop2routes
        candidates = stop2routes(stop_id) & stop2routes(self._last_stop)
        for stop, _ in self._arrivals:
            candidates &= stop2routes(stop)

        if len(candidates) == 1:

            # todo: reset only part of information about trip; already collected stop times should be correct
            self._reset(entity)

            if self.stat_tracker: self.stat_tracker.fix_result["fixed"] += 1
            return

        if len(candidates) == 0:
            self._reset(entity)
            if self.stat_tracker: self.stat_tracker.fix_result["failed"] += 1
        else:  # multiple candidates
            self._fix_state = True
            self._candidate_routes = candidates

    def _narrow_candidates(self, entity):
        stop_id = ext.get_stop_id(entity)
        self._candidate_routes &= self.informant.stop2routes(stop_id)

        if len(self._candidate_routes) == 0:
            self._reset(entity)
            if self.stat_tracker: self.stat_tracker.fix_result["failed"] += 1
            return

        if len(self._candidate_routes) == 1:

            # todo: reset only part of information about trip; already collected stop times should be correct
            self._reset(entity)

            if self.stat_tracker: self.stat_tracker.fix_result["fixed"] += 1

    def _reset(self, entity):
        self.save_delays()
        self._init_dynamic_info(entity)

    # # other
    def _route_check(self, entity):
        if self._broken:
            return
        try:
            trip_id = ext.get_trip_id(entity)
            if self._route != self.informant.trip2route(trip_id):
                if self.stat_tracker: self.stat_tracker.route_change += 1
        except KeyError:
            pass

    def _stop_changed(self, stop_id):
        return self._last_stop != stop_id
