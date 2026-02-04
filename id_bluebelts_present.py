"""
Blue Zone Analysis — PRESENT (intersections, merges, and spatial join)

Purpose
-------
Load processed PRESENT layers (311 points, current moderate flood, 100-year flood), intersect with masked
atomic polygons, aggregate by unique_id, and export dissolved CSVs and a final union CSV.

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
atomic_polygons_path       = path_from_env("ATOMIC_POLYGONS_PATH",         "Mask/atomic_regular_State.shp")
present_311_path           = path_from_env("PRESENT_311_PATH",            "present/311_flooding_ptp2.shp")
present_moderate_flood_path= path_from_env("PRESENT_MODERATE_FLOOD_PATH", "present/Moderate_current_Flood_poly.shp")
present_100yr_path         = path_from_env("PRESENT_100YR_PATH",          "present/100yr.shp")

# --- Outputs ---
output_directory = output_dir("output_csv/present")
output_directory_shp = shapefile_subdir(output_directory)

# --- Load data ---
atomic_polygons = gpd.read_file(atomic_polygons_path)
present_311 = gpd.read_file(present_311_path)
present_moderate_flood = gpd.read_file(present_moderate_flood_path)
present_100yr = gpd.read_file(present_100yr_path)
print('Present layers loaded')

desired_crs = pyproj.CRS.from_epsg(2263)
atomic_polygons = atomic_polygons.to_crs(desired_crs)
atomic_polygons['area'] = atomic_polygons.geometry.area

intersection_dict = {}
new_field_names = []
dissolved_csv_filenames = []

shapefiles_present = [
    {'gdf': present_311,             'flag_field': 'depcall'},
    {'gdf': present_moderate_flood,  'flag_field': 'mod_cur'},
    {'gdf': present_100yr,           'flag_field': '100yr'},
]
print('Present shapefile list created')

# Only process polygon layers for area-based intersections (skip index 0 which is 311 points)
for idx, shapefile_present in enumerate(shapefiles_present[1:], start=1):
    gdf = shapefile_present['gdf'].to_crs(desired_crs)
    intersection_result = gpd.overlay(atomic_polygons, gdf, how='intersection')

    new_field_name = shapefile_present['flag_field'][:-2] + 'A'
    new_field_names.append(new_field_name)

    intersection_result[new_field_name] = intersection_result['geometry'].area

    shp_filename = output_directory_shp / f"{shapefile_present['flag_field']}_notdissolved.shp"
    intersection_result.to_file(shp_filename)

    df = pd.DataFrame(intersection_result)

    if idx == 1:
        dissolved_df = df.groupby('unique_id').agg({
            new_field_name: 'sum',
            shapefile_present['flag_field']: 'first',
            'mo_cu_fldC': 'first'
        }).reset_index()
    else:
        dissolved_df = df.groupby('unique_id').agg({
            new_field_name: 'sum',
            shapefile_present['flag_field']: 'first',
        }).reset_index()

    csv_filename = output_directory / f"{shapefile_present['flag_field']}_dissolved.csv"
    dissolved_df.to_csv(csv_filename, index=False)
    dissolved_csv_filenames.append(csv_filename)
    print(f"Exported {csv_filename.name}")

# Dissolve 311 points by unique_id (no area calc needed)
present_311_df = pd.DataFrame(present_311)
# Keep only necessary columns if present
keep_cols = [c for c in ['unique_id', 'depcall', 'Point_Coun'] if c in present_311_df.columns]
present_311_csv = present_311_df[keep_cols].groupby('unique_id').agg({
    'depcall': 'first' if 'depcall' in keep_cols else 'first',
    'Point_Coun': 'first' if 'Point_Coun' in keep_cols else 'first',
}).reset_index()

# Merge dissolved CSVs + 311
dataframes = [pd.read_csv(p) for p in dissolved_csv_filenames]
dataframes.append(present_311_csv)

final_df = dataframes[0]
suffix_counter = 0
for df in dataframes[1:]:
    suffix_counter += 1
    suffix = f"_{suffix_counter}"
    final_df = final_df.merge(df, on='unique_id', how='outer', suffixes=(suffix, suffix))

atomic_poly_csv = pd.DataFrame(atomic_polygons)
final_df = atomic_poly_csv.merge(final_df, on='unique_id', how='left', suffixes=('_x', '_y'))

# 311 threshold flag
final_df['depcaAfg'] = 0
if 'Point_Coun' in final_df.columns:
    final_df.loc[final_df['Point_Coun'] >= 3, 'depcaAfg'] = 1

# Area-based flags
for n in new_field_names:
    threshold = 0.10 * final_df['area']
    new_flag = n + 'fg'
    final_df[new_flag] = (final_df[n] >= threshold).astype(int)

final_df['BZ_present'] = 0
final_df.loc[
    (final_df.get('depcaAfg', 0) == 1) |
    (final_df.get('mod_cAfg', 0) == 1) |
    (final_df.get('100Afg',   0) == 1), 'BZ_present'] = 1

final_output_csv = output_directory / 'present_union.csv'
final_df.to_csv(final_output_csv, index=False, header=True)
print(f"Final CSV saved: {final_output_csv}")
