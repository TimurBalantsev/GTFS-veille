class Tile:
    def __init__(self, geo_polygon):
        self.geo_polygon = geo_polygon
        self.bus_stops = None

    def add_bus_stop(self, bus_stop):
        self.bus_stops = bus_stop
