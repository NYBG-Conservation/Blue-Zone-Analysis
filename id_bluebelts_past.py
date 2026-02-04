"""
Blue Zone Analysis — PAST (intersections, merges, and spatial join)

Purpose
-------
Load PAST (Welikia) historical ecology layers, intersect with masked atomic polygons, aggregate by
unique_id, and export dissolved CSVs and a final union CSV.

Path Configuration
------------------
All paths are configurable via environment variables (see common_paths.py). Sensible project-relative
defaults are provided so the script can run with a conventional layout.
"""
import os
from pathlib import Path
import geopandas as gpd
import pandas as pd
import pyproj

from common_paths import path_from_env, output_dir, shapefile_subdir

# --- Input paths ---
atomic_polygons_path   = path_from_env("ATOMIC_POLYGONS_PATH",   "Mask/atomic_regular_State.shp")
past_beaches_path      = path_from_env("PAST_BEACHES_PATH",      "historical/beach.shp")
past_river_path        = path_from_env("PAST_RIVER_PATH",        "historical/river.shp")
past_freshwetl_path    = path_from_env("PAST_FRESHWETL_PATH",    "historical/fresh_wetland.shp")
past_marine_path       = path_from_env("PAST_MARINE_PATH",       "historical/marine_water.shp")
past_pond_path         = path_from_env("PAST_POND_PATH",         "historical/ponds.shp")
past_saltmarsh_path    = path_from_env("PAST_SALTMARSH_PATH",    "historical/saltmarsh.shp")
past_streams_path      = path_from_env("PAST_STREAMS_PATH",      "historical/streams_buffered.shp")
past_dunes_path        = path_from_env("PAST_DUNES_PATH",        "historical/dunes.shp")
past_tidalcreek_path   = path_from_env("PAST_TIDALCREEK_PATH",   "historical/tidal_creek.shp")
past_intstream_path    = path_from_env("PAST_INTSTREAM_PATH",    "historical/int_stream.shp")

# --- Outputs ---
output_directory = output_dir("output_csv/past")
output_directory_shp = shapefile_subdir(output_directory)

# --- Load data ---
atomic_polygons = gpd.read_file(atomic_polygons_path)
past_beaches = gpd.read_file(past_beaches_path)
past_freshwater_river = gpd.read_file(past_river_path)
past_freshwater_wetlands = gpd.read_file(past_freshwetl_path)
past_marine_water = gpd.read_file(past_marine_path)
past_pond = gpd.read_file(past_pond_path)
past_saltmarsh = gpd.read_file(past_saltmarsh_path)
past_streams_buffer15 = gpd.read_file(past_streams_path)
past_dune = gpd.read_file(past_dunes_path)
past_tidal_creek = gpd.read_file(past_tidalcreek_path)
past_intermit = gpd.read_file(past_intstream_path)
print('Past layers loaded')

desired_crs = pyproj.CRS.from_epsg(2263)
atomic_polygons = atomic_polygons.to_crs(desired_crs)
atomic_polygons['area'] = atomic_polygons.geometry.area

new_field_names = []
dissolved_csv_filenames = []

shapefiles_past = [
    {'gdf': past_beaches,               'flag_field': 'beaches'},
    {'gdf': past_freshwater_river,      'flag_field': 'river'},
    {'gdf': past_freshwater_wetlands,   'flag_field': 'fresh_wetl'},
    {'gdf': past_marine_water,          'flag_field': 'marine'},
    {'gdf': past_pond,                  'flag_field': 'pond'},
    {'gdf': past_saltmarsh,             'flag_field': 'saltmarsh'},
    {'gdf': past_streams_buffer15,      'flag_field': 'streams'},
    {'gdf': past_dune,                  'flag_field': 'dunes'},
    {'gdf': past_tidal_creek,           'flag_field': 'tidal_cree'},
    {'gdf': past_intermit,              'flag_field': 'int_stream'},
]
print('Past shapefile list created')

for shapefile_past in shapefiles_past:
    gdf = shapefile_past['gdf'].to_crs(desired_crs)
    intersection_result = gpd.overlay(atomic_polygons, gdf, how='intersection')

    new_field_name = shapefile_past['flag_field'][:-2] + 'A'
    new_field_names.append(new_field_name)

    intersection_result[new_field_name] = intersection_result['geometry'].area

    # Optional: write dissolved SHP for QA
    dissolved_gdf = intersection_result.dissolve(by='unique_id', aggfunc={new_field_name: 'sum', shapefile_past['flag_field']:'first'}, as_index=False)
    shp_filename = output_directory_shp / f"{shapefile_past['flag_field']}_dissolved.shp"
    dissolved_gdf.to_file(shp_filename)

    # Export per-layer dissolved CSV
    df = pd.DataFrame(intersection_result)
    dissolved_df = df.groupby('unique_id').agg({
        new_field_name: 'sum',
        shapefile_past['flag_field']:'first'
    }).reset_index()

    csv_filename = output_directory / f"{shapefile_past['flag_field']}_dissolved.csv"
    dissolved_df.to_csv(csv_filename, index=False)
    dissolved_csv_filenames.append(csv_filename)
    print(f"Exported {csv_filename.name}")

# Merge dissolved CSVs on unique_id
print(new_field_names)

dataframes = [pd.read_csv(p) for p in dissolved_csv_filenames]
final_df = dataframes[0]
suffix_counter = 0
for df in dataframes[1:]:
    suffix_counter += 1
    suffix = f"_{suffix_counter}"
    final_df = final_df.merge(df, on='unique_id', how='outer', suffixes=(suffix, suffix))

# Compute past_sum, join area, then BZ_past
atomic_poly_csv = pd.DataFrame(atomic_polygons)
final_df['past_sum'] = final_df[new_field_names].sum(axis=1)
final_df = atomic_poly_csv.merge(final_df, on='unique_id', how='left', suffixes=('_x', '_y'))

threshold = 0.10 * final_df['area']
final_df['BZ_past'] = (final_df['past_sum'] >= threshold).astype(int)

final_output_csv = output_directory / 'past_union.csv'
final_df.to_csv(final_output_csv, index=False)
print(f"Final CSV saved: {final_output_csv}")
