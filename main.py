import copy

import geopandas
import gtfs_kit as gk
from path import Path
from tile_generator import generate_tiles, polygon_from_long_lat
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image


def flatten_list(l):
    return [item for sublist in l for item in sublist]


starting_longitude = -73.612569
starting_latitude = 45.449341

ending_longitude = -73.592915
ending_latitude = 45.430836

time_segments = [["12:00:00", "13:00:00"], ["17:00:00", "18:00:00"]]

long_lat_crs = "EPSG:4326"
dist_units = "km"
# in km
tile_size = 0.1

tiles = generate_tiles(starting_longitude, starting_latitude, ending_longitude, ending_latitude, tile_size)
flattened_tiles = flatten_list(tiles)

d = {'coords': ['polygon'],
     'geometry': [polygon_from_long_lat(starting_latitude, starting_longitude, ending_latitude, ending_longitude)]}
gdf = geopandas.GeoDataFrame(d, crs=long_lat_crs)

gtfs_path = Path('./gtfs_stm.zip')

feed = (gk.read_feed(gtfs_path, dist_units=dist_units))

stop_times = feed.stop_times
stops = feed.get_stops_in_area(gdf)


def format_time(time):
    time = time.split(':')
    return ' '.join(time)


def time_to_seconds(time):
    hours, minute, seconds = time.split(':')
    return int(hours) * 3600 + int(minute) * 60 + int(seconds)


def validate_departure_time(time, time_segment):
    count = 0
    min_secs = time_to_seconds(time_segment[0])
    max_secs = time_to_seconds(time_segment[1])

    for departure_time in time.departure_time:
        if min_secs <= time_to_seconds(departure_time) <= max_secs:
            count = count + 1

    return count


def find_stop_times(stop_id):
    return stop_times[(stop_times.stop_id == stop_id)]


for tile in flattened_tiles:
    tile_stops = feed.get_stops_in_area(tile.geo_polygon)
    tile.add_bus_stop(tile_stops)
    for index, stop in tile_stops.iterrows():
        cur_stop_times = find_stop_times(stop.stop_id)

for time_segment in time_segments:
    bus_stop_per_tile = copy.deepcopy(tiles)

    for i in range(len(bus_stop_per_tile)):
        for j in range(len(bus_stop_per_tile[i])):
            count = 0
            for index, stop in bus_stop_per_tile[i][j].bus_stops.iterrows():
                count = count + validate_departure_time(find_stop_times(stop.stop_id), time_segment)
            bus_stop_per_tile[i][j] = count

    sns.set_palette("Paired")
    ax = sns.heatmap(bus_stop_per_tile, alpha=0.5, zorder=2)
    img = mpimg.imread('Capture.PNG')
    ax.imshow(img, aspect='auto', extent=ax.get_xlim() + ax.get_ylim(), zorder=1)
    plt.savefig(f'{format_time(time_segment[0])}-{format_time(time_segment[1])}.png')
    plt.clf()

imageList = []

for time_seg in time_segments:
    imageList.append(Image.open(f'{format_time(time_seg[0])}-{format_time(time_seg[1])}.png'))

duration = 500

imageList[0].save('produit.gif', save_all=True, append_images=imageList[1:], duration=duration, loop=0)
