"""
Past Layer Preprocessing — Welikia → Analysis-Ready

Purpose
-------
Normalize raw Welikia (past) layers to a common CRS (EPSG:2263), drop extraneous
attributes, add binary flags, optionally buffer line features, and write the
standardized shapefiles that downstream Blue Zone scripts expect.

Path Configuration
------------------
Prefer environment variables; otherwise defaults assume a conventional
project-relative layout.

Environment variables (optional)
--------------------------------
# Inputs (raw Welikia vectors)
PAST_RAW_DIR               -> base folder of raw Welikia vectors (default: ./welikia_raw)
  or override each file directly:
FRESH_RIVER_PATH           -> Freshwater_rivers_v8_0.shp
FRESH_WETLANDS_PATH        -> Freshwater_wetlands_v8_0.shp
MARINE_WATER_PATH          -> Marine_waters_MTL_mw30_60_poly.shp
PONDS_PATH                 -> Ponds_v8_0.shp
SALTMARSH_PATH             -> Tidal_marshes_mw664_00.shp
STREAMS_PATH               -> Streams_upland_line_v8_0.shp
TIDAL_CREEKS_PATH          -> Tidal_creeks_v8_0.shp
SURFICIAL_GEOLOGY_PATH     -> Surficial_geology_v8_0.shp
BEACHES_PATH               -> Beaches_mw659_00.shp

# Outputs
BLUEZONES_OUTPUT_DIR       -> root output directory (default: ./output_csv)
PAST_PROCESSED_DIR         -> specific output subdir for past layers
                             (default: <BLUEZONES_OUTPUT_DIR>/past)

Notes
-----
- Only the streams and tidal creeks buffering steps are active by default to match
  the original script. Other layers are scaffolded below; un-comment to export them.
- EPSG:2263 (NAD83 / New York Long Island (ftUS)) is used for area/length in feet.
"""
from __future__ import annotations
import os
from pathlib import Path
import geopandas as gpd
import pyproj

# ------------------------- path helpers -------------------------

def _base_dir() -> Path:
    return Path(os.getenv("BLUEZONES_BASE_DIR", ".")).resolve()


def _path_from_env(env_var: str, default_relative: str, root: Path | None = None) -> Path:
    p = os.getenv(env_var)
    if p:
        return Path(p)
    root = root if root is not None else _base_dir()
    return root / default_relative


def _output_dir() -> Path:
    out_root = Path(os.getenv("BLUEZONES_OUTPUT_DIR", _base_dir() / "output_csv"))
    specific = os.getenv("PAST_PROCESSED_DIR")
    if specific:
        p = Path(specific)
    else:
        p = out_root / "past"
    p.mkdir(parents=True, exist_ok=True)
    return p

# ------------------------- configure inputs -------------------------
PAST_RAW_DIR = Path(os.getenv("PAST_RAW_DIR", _base_dir() / "welikia_raw"))

freshwater_river_path   = _path_from_env("FRESH_RIVER_PATH",       "Vector/Freshwater_rivers_v8_0.shp",      PAST_RAW_DIR)
freshwater_wet_path     = _path_from_env("FRESH_WETLANDS_PATH",    "Vector/Freshwater_wetlands_v8_0.shp",   PAST_RAW_DIR)
marine_water_path       = _path_from_env("MARINE_WATER_PATH",      "Vector/Marine_waters_MTL_mw30_60_poly.shp", PAST_RAW_DIR)
ponds_path              = _path_from_env("PONDS_PATH",             "Vector/Ponds_v8_0.shp",                  PAST_RAW_DIR)
saltmarsh_path          = _path_from_env("SALTMARSH_PATH",         "Vector/Tidal_marshes_mw664_00.shp",      PAST_RAW_DIR)
streams_path            = _path_from_env("STREAMS_PATH",           "Vector/Streams_upland_line_v8_0.shp",    PAST_RAW_DIR)
tidal_creeks_path       = _path_from_env("TIDAL_CREEKS_PATH",      "Vector/Tidal_creeks_v8_0.shp",           PAST_RAW_DIR)
surficial_geology_path  = _path_from_env("SURFICIAL_GEOLOGY_PATH", "Vector/Surficial_geology_v8_0.shp",      PAST_RAW_DIR)
beaches_path            = _path_from_env("BEACHES_PATH",           "Vector/Beaches_mw659_00.shp",            PAST_RAW_DIR)

# ------------------------- outputs -------------------------
FINAL_DIR = _output_dir()

# ------------------------- constants -------------------------
desired_crs = pyproj.CRS.from_epsg(2263)

# ------------------------- load inputs -------------------------
print("Loading Welikia layers…")
freshwater_river   = gpd.read_file(freshwater_river_path)
freshwater_wetlands= gpd.read_file(freshwater_wet_path)
marine_water       = gpd.read_file(marine_water_path)
ponds              = gpd.read_file(ponds_path)
saltmarsh          = gpd.read_file(saltmarsh_path)
streams            = gpd.read_file(streams_path)
tidal_creek_a      = gpd.read_file(tidal_creeks_path)
surficial_geology  = gpd.read_file(surficial_geology_path)
beaches            = gpd.read_file(beaches_path)
print("Welikia layers loaded")

# ------------------------- processing -------------------------
# Helper to reproject and keep only geometry + flag

def _flag_and_minify(gdf: gpd.GeoDataFrame, flag_name: str) -> gpd.GeoDataFrame:
    gdf = gdf.to_crs(desired_crs)
    gdf[flag_name] = 1
    return gdf[["geometry", flag_name]]

# ---- STREAMS (buffer 15 ft) ----
flag_field = 'streams'
streams = streams.to_crs(desired_crs)
streams[flag_field] = 1
upland = gpd.GeoDataFrame({'geometry': streams.geometry.buffer(15), 'streams': 1}, crs=desired_crs)
filename = FINAL_DIR / 'streams_buffered.shp'
upland.to_file(filename)
print(f"Wrote: {filename}")

# ---- TIDAL CREEKS (buffer 15 ft) ----
flag_field = 'tidal_cree'
tidal_creek_a = tidal_creek_a.to_crs(desired_crs)
tidal_creek_a[flag_field] = 1
tidal_creek = gpd.GeoDataFrame({'geometry': tidal_creek_a.geometry.buffer(15), 'tidal_cree': 1}, crs=desired_crs)
filename = FINAL_DIR / 'tidal_creek.shp'
tidal_creek.to_file(filename)
print(f"Wrote: {filename}")

# ---- OPTIONAL EXPORTS (uncomment as needed) ----
# river = _flag_and_minify(freshwater_river, 'river')
# river.to_file(FINAL_DIR / 'river.shp')

# fresh_wetland = _flag_and_minify(freshwater_wetlands, 'fresh_wetl')
# fresh_wetland.to_file(FINAL_DIR / 'fresh_wetland.shp')

# marine = _flag_and_minify(marine_water, 'marine')
# marine.to_file(FINAL_DIR / 'marine_water.shp')

# natural_ponds = ponds[ponds.get('Manmade', 0) == 0]
# ponds_out = _flag_and_minify(natural_ponds, 'pond')
# ponds_out.to_file(FINAL_DIR / 'ponds.shp')

# saltmarsh_out = _flag_and_minify(saltmarsh, 'saltmarsh')
# saltmarsh_out.to_file(FINAL_DIR / 'saltmarsh.shp')

# dunes_raw = surficial_geology.to_crs(desired_crs)
# dunes_raw = dunes_raw[dunes_raw.get('Actv_Dune', 0) == 1]
# dunes_out = dunes_raw[['geometry']].copy()
# dunes_out['dunes'] = 1
# dunes_out.to_file(FINAL_DIR / 'dunes.shp')

# beaches_out = _flag_and_minify(beaches, 'beaches')
# beaches_out.to_file(FINAL_DIR / 'beach.shp')

print("Past preprocessing complete.")
