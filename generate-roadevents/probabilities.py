import random


class NoEvent:
    """NoEvent probability"""
    def __init__(self, road_type, voivodeship, noincident, noaccident):
        self.road_type = road_type
        self.voivodeship = voivodeship
        self.no_incident_prob = noincident
        self.no_accident_prob = noaccident
        self.bk = road_type + '-' + voivodeship

    def __str__(self):
        return self.bk + ' => ' + 'No Incident: ' + self.no_incident_prob + '% ' + 'No Accident: ' + self.no_accident_prob


class IncidentProbability:
    """Incident Probability and Distribution"""
    def __init__(self, event_name, road_type, no_event, count_mean, count_stdev):
        self.event_name = event_name
        self.road_type = road_type
        self.no_event = no_event
        self.count_mean = count_mean
        self.count_stdev = count_stdev
        self.bk = self.event_name + ':' + self.road_type

    def random_count(self):
        cnt = round(random.normalvariate(int(self.count_mean), int(self.count_stdev)), 0)
        if cnt <= 0:
            cnt = 1
        return cnt

    def bk(self):
        return str(self.event_name + ':' + self.road_type)


class AccidentProbability:
    """Accident Probability and Distribution"""
    def __init__(self, event_name, road_type, no_event, count_mean, count_stdev, injured_mean, injured_stdev, killed_mean, killed_stdev):
        self.event_name = event_name
        self.road_type = road_type
        self.no_event = no_event
        self.count_mean = count_mean
        self.count_stdev = count_stdev
        self.injured_mean = injured_mean
        self.injured_stdev = injured_stdev
        self.killed_mean = killed_mean
        self.killed_stdev = killed_stdev
        self.bk = self.event_name + ':' + self.road_type

    def random_count(self):
        cnt = int(round(random.normalvariate(int(self.count_mean), int(self.count_stdev)), 0))
        if cnt <= 0:
            cnt = 1
        return cnt

    def random_injured(self):
        injured = int(round(random.normalvariate(int(self.injured_mean), int(self.injured_stdev)), 0))
        if injured < 0:
            injured = 0
        return injured

    def random_killed(self):
        killed = int(round(random.normalvariate(int(self.killed_mean), int(self.killed_stdev)), 0))
        if killed < 0:
            killed = 0
        return killed

    def bk(self):
        return str(self.event_name + ':' + self.road_type)