"""
Common path utilities for BlueZones scripts.

Usage:
- Set environment variables to point to your data folders or override individual file paths.
- Defaults fall back to a conventional relative layout under the project root.

Environment variables (optional):
  BLUEZONES_BASE_DIR          -> base directory for all data (e.g., /data/BlueZones)
  BLUEZONES_OUTPUT_DIR        -> output directory for CSVs and shapefiles

Per-file overrides (optional):
  ATOMIC_POLYGONS_PATH
  PRESENT_311_PATH
  PRESENT_MODERATE_FLOOD_PATH
  PRESENT_100YR_PATH
  FUTURE_MOD_2050_PATH
  FUTURE_EXT_2080_PATH
  FUTURE_500YR_PATH
  PAST_BEACHES_PATH
  PAST_RIVER_PATH
  PAST_FRESHWETL_PATH
  PAST_MARINE_PATH
  PAST_POND_PATH
  PAST_SALTMARSH_PATH
  PAST_STREAMS_PATH
  PAST_DUNES_PATH
  PAST_TIDALCREEK_PATH
  PAST_INTSTREAM_PATH
"""
from __future__ import annotations
import os
from pathlib import Path


def base_dir() -> Path:
    return Path(os.getenv("BLUEZONES_BASE_DIR", ".")).resolve()


def output_dir(default_subdir: str) -> Path:
    # Allow either a global override or per-script default
    od = os.getenv("BLUEZONES_OUTPUT_DIR")
    if od:
        p = Path(od)
    else:
        p = base_dir() / default_subdir
    p.mkdir(parents=True, exist_ok=True)
    return p


def shapefile_subdir(parent: Path) -> Path:
    shp = parent / "shapefiles"
    shp.mkdir(parents=True, exist_ok=True)
    return shp


def path_from_env(var: str, relative_default: str) -> Path:
    # If env var provided, use it; else join base_dir with relative_default
    p = os.getenv(var)
    if p:
        return Path(p)
    return base_dir() / relative_default
