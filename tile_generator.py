import math

import geopandas

from tile import Tile
from shapely.geometry import Polygon, Point

r_earth = 6378
long_lat_crs = "EPSG:4326"


def increment_lat(lat, size):
    return lat + ((size / r_earth) * (180 / math.pi))


def decrement_lat(lat, size):
    return lat - ((size / r_earth) * (180 / math.pi))


def increment_long(long, lat, size):
    return long + (size / r_earth) * (180 / math.pi) / math.cos(lat * math.pi / 180)


def decrement_long(long, lat, size):
    return long - (size / r_earth) * (180 / math.pi) / math.cos(lat * math.pi / 180)


def polygon_from_long_lat(starting_lat, starting_long, ending_lat, ending_long):
    coords = (
        (starting_long, starting_lat), (starting_long, ending_lat), (ending_long, ending_lat),
        (ending_long, starting_lat))
    return Polygon(coords)


def create_tile_from_lat_long(long, lat, size, lat_desc, long_desc):
    start_long = long
    start_lat = lat

    if long_desc:
        end_long = decrement_long(long, lat, size)
    else:
        end_long = increment_long(long, lat, size)

    if lat_desc:
        end_lat = decrement_lat(lat, size)
    else:
        end_lat = increment_lat(lat, size)

    d = {'coords': ['polygon'],
         'geometry': [polygon_from_long_lat(start_lat, start_long, end_lat, end_long)]}

    gdf = geopandas.GeoDataFrame(d, crs=long_lat_crs)

    return Tile(gdf)


def is_end_of_row(curr_lat, ending_lat, descending):
    if descending:
        return curr_lat < ending_lat
    else:
        return curr_lat > ending_lat


def is_end_of_column(curr_long, ending_long, descending):
    if descending:
        return curr_long < ending_long
    else:
        return curr_long > ending_long


def generate_tiles(starting_longitude, starting_latitude, ending_longitude, ending_latitude, tile_size):
    is_tile_remaining = True
    tiles = []
    temp_arr = []

    lat_descending = False
    long_descending = False

    if ending_latitude < starting_latitude:
        lat_descending = True

    if ending_longitude < starting_longitude:
        long_descending = True

    curr_long = starting_longitude
    curr_lat = starting_latitude

    while is_tile_remaining:

        if long_descending:
            curr_long = decrement_long(curr_long, curr_lat, tile_size)
        else:
            curr_long = increment_long(curr_long, curr_lat, tile_size)

        temp_arr.append(create_tile_from_lat_long(curr_long, curr_lat, tile_size, lat_descending, long_descending))

        if is_end_of_column(curr_long, ending_longitude, long_descending):
            curr_long = starting_longitude

            if lat_descending:
                curr_lat = decrement_lat(curr_lat, tile_size)
            else:
                curr_lat = increment_lat(curr_lat, tile_size)

            tiles.append([*temp_arr])
            temp_arr.clear()

        if is_end_of_row(curr_lat, ending_latitude, lat_descending):
            is_tile_remaining = False
    return tiles
