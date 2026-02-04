"""
Blue Zone Analysis — FUTURE (intersections, merges, and spatial join)

Purpose
-------
Load processed FUTURE flood layers, intersect with masked atomic polygons, aggregate by unique_id,
and export dissolved CSVs and a final union CSV.

Path Configuration
------------------
All paths are configurable via environment variables (see common_paths.py). Sensible project-relative
defaults are provided so the script can run out-of-the-box with a conventional layout.
"""
import os
from pathlib import Path
import geopandas as gpd
import pandas as pd
import pyproj

from common_paths import path_from_env, output_dir, shapefile_subdir

# --- Input paths (override via env vars if needed) ---
atomic_polygons_path = path_from_env("ATOMIC_POLYGONS_PATH", "Mask/atomic_regular_State.shp")
future_mod_2050_path = path_from_env("FUTURE_MOD_2050_PATH", "future_flooding/Moderate_2050_Flood_poly.shp")
future_ext_2080_path = path_from_env("FUTURE_EXT_2080_PATH", "future_flooding/Extreme_2080_Flood_poly.shp")
future_500yr_path    = path_from_env("FUTURE_500YR_PATH",    "future_flooding/500yr.shp")

# --- Outputs ---
output_directory = output_dir("output_csv/future")
output_directory_shp = shapefile_subdir(output_directory)

# --- Load data ---
atomic_polygons = gpd.read_file(atomic_polygons_path)
future_moderate_2050_flood = gpd.read_file(future_mod_2050_path)
future_extreme_2080_flood  = gpd.read_file(future_ext_2080_path)
future_500yr               = gpd.read_file(future_500yr_path)
print('Future layers loaded')

desired_crs = pyproj.CRS.from_epsg(2263)
atomic_polygons = atomic_polygons.to_crs(desired_crs)
atomic_polygons['area'] = atomic_polygons.geometry.area

intersection_dict = {}
new_field_names = []
dissolved_csv_filenames = []

shapefiles_future = [
    {'gdf': future_moderate_2050_flood, 'flag_field': 'mod_2050', 'flood_type': 'mo_20_fldC'},
    {'gdf': future_extreme_2080_flood,  'flag_field': 'ext_2080', 'flood_type': 'ex_20_fldC'},
    {'gdf': future_500yr,               'flag_field': '500yr'},
]
print('Future shapefile list created')

count = 0
for shapefile_future in shapefiles_future:
    gdf = shapefile_future['gdf'].to_crs(desired_crs)
    intersection_result = gpd.overlay(atomic_polygons, gdf, how='intersection')

    new_field_name = shapefile_future['flag_field'][:-2] + 'A'
    new_field_names.append(new_field_name)

    # area in feet (assuming CRS in feet; EPSG:2263 is US ft)
    intersection_result[new_field_name] = intersection_result['geometry'].area

    # Save intermediate (not dissolved) shapefile for QA
    shp_filename = output_directory_shp / f"{shapefile_future['flag_field']}_notdissolved.shp"
    intersection_result.to_file(shp_filename)

    # Export per-layer dissolved CSV
    df = pd.DataFrame(intersection_result)
    if count <= 1 and 'flood_type' in shapefile_future:
        dissolved_df = df.groupby('unique_id').agg({
            new_field_name: 'sum',
            shapefile_future['flag_field']: 'first',
            shapefile_future['flood_type']: 'first'
        }).reset_index()
    else:
        dissolved_df = df.groupby('unique_id').agg({
            new_field_name: 'sum',
            shapefile_future['flag_field']: 'first'
        }).reset_index()
    count += 1

    csv_filename = output_directory / f"{shapefile_future['flag_field']}_dissolved.csv"
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

# Join atomic polygon area
atomic_poly_csv = pd.DataFrame(atomic_polygons)
final_df = atomic_poly_csv.merge(final_df, on='unique_id', how='left', suffixes=('_x', '_y'))

# Flag thresholds per layer and compute BZ_future
for n in new_field_names:
    threshold = 0.10 * final_df['area']
    new_flag = n + 'fg'
    final_df[new_flag] = (final_df[n] >= threshold).astype(int)

final_df['BZ_future'] = 0
final_df.loc[
    (final_df.get('mod_20Afg', 0) == 1) |
    (final_df.get('ext_20Afg', 0) == 1) |
    (final_df.get('500Afg',   0) == 1), 'BZ_future'] = 1

final_output_csv = output_directory / 'future_union.csv'
final_df.to_csv(final_output_csv, index=False, header=True)
print(f"Final CSV saved: {final_output_csv}")
