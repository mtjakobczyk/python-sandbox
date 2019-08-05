class LocationDim:
    """Location Dimension"""
    def __init__(self, location_id, road_nb, road_type, voivodeship):
        self.location_id = location_id
        self.road_nb = road_nb
        self.road_type = road_type
        self.voivodeship = voivodeship

    def getbk(self):
        return self.road_type + '-' + self.voivodeship


class RoadEventDim:
    """Road Event Dimension"""
    def __init__(self, road_event_id, road_event_name, road_event_category):
        self.id = road_event_id
        self.name = road_event_name
        self.category = road_event_category
