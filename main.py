import geopandas
import gtfs_kit as gk
from path import Path
from shapely.geometry import Polygon, Point

starting_longitude = -73.612569
starting_latitude = 45.449341

ending_longitude = -73.601482
ending_latitude = 45.433446

long_lat_crs = "EPSG:4326"
dist_units = "km"
# in meters
tile_size = 100


def polygon_from_long_lat(starting_lat, starting_long, ending_lat, ending_long):
    coords = (
        (starting_long, starting_lat), (starting_long, ending_lat), (ending_long, ending_lat),
        (ending_long, starting_lat))
    return Polygon(coords)


d = {'coords': ['polygon'],
     'geometry': [polygon_from_long_lat(starting_latitude, starting_longitude, ending_latitude, ending_longitude)]}
gdf = geopandas.GeoDataFrame(d, crs=long_lat_crs)

gtfs_path = Path('./gtfs_stm.zip')

feed = (gk.read_feed(gtfs_path, dist_units=dist_units))

stops = feed.get_stops_in_area(gdf)

# TODO add a function that cuts up the long lat into tiles of given length and creates an object with the bus stop inside

print(stops)
