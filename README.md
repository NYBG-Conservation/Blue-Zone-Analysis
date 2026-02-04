# Blue Zones NYC: Historical Ecology and Flood Risk Analysis

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains the analysis code for identifying "Blue Zones" in New York City - areas that were historically wet (pre-1609), currently flood, and are predicted to flood in the future under climate change scenarios. 

**Associated Publication:**  
*"Blue Zones: Identifying adaptation opportunities using past, present, and future flooding in New York City"*  
Lucinda Royte & Eric W. Sanderson  
New York Botanical Garden, 2026

## Overview

Water has memory. Despite 400 years of urbanization, flood-prone areas in NYC often align with historical hydrology - former streams, wetlands, and tidal marshes. This project combines:

- **Historical ecology** data from the Welikia Project (c. 1609 ecosystems)
- **Current flooding** observations (311 calls, DEP stormwater models, FEMA zones)
- **Future projections** climate change scenarios for 2050 and 2080 (DEM stormwater models, FEMA zones)

The analysis identifies 538 Blue Zones covering 21% of NYC's land area, affecting approximately 1.2 million people and 11% of city buildings.

## Output Data

### Final Blue Zones Shapefile/CSV

The analysis produces a dataset with these key fields:

- **`BZ`** - Blue Zone flag (1 = past AND present AND future flooding)
- **`BZ_past`** - Historical flooding flag (≥10% was pre-1609 aquatic ecosystems)
- **`BZ_present`** - Current flooding flag (≥10% floods OR ≥3 311 calls)
- **`BZ_future`** - Future flooding flag (≥10% predicted to flood)
- **`unique_id`** - Block identifier
- **`gridcode`** - Blue Zone id identifier

### Data Access

- **NYC Open Data**: https://opendata.cityofnewyork.us/
- **Welikia Project Historic Ecology**: Contact authors for data sharing agreement or visit welikia.org

## Usage

### Analysis Workflow

The analysis follows this sequence:

```bash
# 1. Process historical ecology layers
python scripts/past_processing.py

# 2. Identify historical flooding (past)
python scripts/id_bluebelts_past.py

# 3. Identify current flooding (present)
python scripts/id_bluebelts_present.py

# 4. Identify future flooding projections
python scripts/id_bluebelts_future.py

# 5. Merge all temporal analyses into final Blue Zones
python scripts/merge_csv.py
```

## Authors

- **Lucinda Royte**  - New York Botanical Garden
  - Email: lroyte@nybg.org
  
- **Eric W. Sanderson** -  New York Botanical Garden


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Data Availability
Historical ecology datasets from the Welikia Project require a data sharing agreement with the New York Botanical Garden.


## Questions or Issues?

- Contact: lroyte@nybg.org or urbanconservation@nybg.org

## Related Resources

- **Welikia Project**: https://welikia.org/
- **Historical Maps**: https://layersofthepast.org/

# DATA DICTIONARY

---


# Blue Zones NYC Data Dictionary

## Overview

This document provides detailed descriptions of all fields in the Blue Zones dataset, including the final shapefile and intermediate CSV outputs.

---

## Final Blue Zones Shapefile

### Spatial Information

| Field | Type | Description |
|-------|------|-------------|
| `geometry` | Polygon | Block boundary geometry (EPSG:2263 - NY State Plane Long Island, feet) |
| `unique_id` | Integer | Unique identifier for each atomic polygon (city block) |
| `area` | Float | Total area of the block in square feet |


| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `BZ_past` | Integer | 0 or 1 | **Historical Flooding Flag**<br>1 = Block was ≥10% covered by pre-1609 aquatic/marine ecosystems<br>0 = Block was mostly upland |
| `BZ_present` | Integer | 0 or 1 | **Current Flooding Flag**<br>1 = Block currently floods (≥10% area flooded OR ≥3 311 calls)<br>0 = Block does not currently flood |
| `BZ_future` | Integer | 0 or 1 | **Future Flooding Flag**<br>1 = Block predicted to flood under climate scenarios (≥10% area)<br>0 = Block not predicted to flood |
| `BZ` | Integer | 0 or 1 | **Blue Zone Flag (MAIN CLASSIFICATION)**<br>1 = Block meets ALL three criteria (past AND present AND future)<br>0 = Block does not meet all three criteria<br><br>**This is the key field identifying priority adaptation areas** |

---
## Intermediate CSV Outputs
## Historical Flooding (Past) Fields

### Ecosystem Area Measurements

All area fields measured in square feet. These represent the overlap between historical ecosystems and each block.

#### Marine and Coastal Ecosystems

| Field | Description | Original Ecosystem Type |
|-------|-------------|------------------------|
| `beachesA` | Area of historical beaches | Sandy beaches along coastline (c. 1609) |
| `marineA` | Area of marine waters | Waters below mean tide level, now mostly landfilled |
| `saltmaA` | Area of tidal salt marshes | High and low salt marshes in intertidal zone |
| `dunesA` | Area of active sand dunes | Coastal dune systems |
| `tidal_cA` | Area of tidal creeks (buffered 15ft) | Tidal waterways and channels |

#### Freshwater Ecosystems

| Field | Description | Original Ecosystem Type |
|-------|-------------|------------------------|
| `riverA` | Area of freshwater rivers | Major river systems |
| `streamsA` | Area of upland streams (buffered 15ft) | Small streams and tributaries |
| `fresh_wA` | Area of freshwater wetlands | Swamps, marshes, wet meadows |
| `pondA` | Area of natural ponds | Natural ponds (excluding manmade) |
| `int_strA` | Area of intermittent streams (buffered 15ft) | Seasonally flowing streams |

### Summary Fields

| Field | Type | Description |
|-------|------|-------------|
| `past_sum` | Float | Total area (sq ft) of all historical aquatic/marine ecosystems in the block<br>Sum of all ecosystem area fields above |


## Current Flooding (Present) Fields

### Flood Type Area Measurements

| Field | Description | Source Data |
|-------|-------------|-------------|
| `mod_cA` | Area (sq ft) flooded in DEP Moderate Current scenario | DEP Stormwater Flood Map: 2 inches rain/hour, current sea level |
| `100A` | Area (sq ft) in FEMA 100-year floodplain | FEMA PFIRM: 1% annual probability coastal flood |

### Flood Type Flags

| Field | Type | Description |
|-------|------|-------------|
| `depcaAfg` | Integer (0/1) | **311 Calls Flag**<br>1 = ≥3 flooding calls reported (2010-2025)<br>0 = <3 calls |
| `mod_cAfg` | Integer (0/1) | **DEP Moderate Current Flag**<br>1 = ≥10% of block area floods in scenario<br>0 = <10% area floods |
| `100Afg` | Integer (0/1) | **FEMA 100-year Flag**<br>1 = ≥10% of block in floodplain<br>0 = <10% in floodplain |

### 311 Call Data

| Field | Type | Description |
|-------|------|-------------|
| `depcall` | Integer (0/1) | Indicates if any 311 flooding calls were made for this block |
| `Point_Count` | Integer | Total number of 311 flooding calls (2010-2025)<br>Null if no calls |

### Flood Classification

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `mo_cu_fldC` | String | Various | DEP flood classification code for moderate current scenario<br>Categories indicate flood depth and type |

---

## Future Flooding Projections Fields

### Climate Scenario Area Measurements

| Field | Description | Scenario Details |
|-------|-------------|-----------------|
| `mod_20A` | Area (sq ft) flooded in 2050 moderate scenario | DEP: 2 inches rain/hour + 2050 sea level rise |
| `ext_20A` | Area (sq ft) flooded in 2080 extreme scenario | DEP: 3.5 inches rain/hour + 2080 sea level rise |
| `500A` | Area (sq ft) in FEMA 500-year floodplain | FEMA: 0.2% annual probability event |

### Climate Scenario Flags

| Field | Type | Description |
|-------|------|-------------|
| `mod_20Afg` | Integer (0/1) | **2050 Moderate Flag**<br>1 = ≥10% of block floods in scenario<br>0 = <10% floods |
| `ext_20Afg` | Integer (0/1) | **2080 Extreme Flag**<br>1 = ≥10% of block floods in scenario<br>0 = <10% floods |
| `500Afg` | Integer (0/1) | **500-year Event Flag**<br>1 = ≥10% of block in floodplain<br>0 = <10% in floodplain |

### Scenario Identification

| Field | Type | Description |
|-------|------|-------------|
| `mod_2050` | Integer (0/1) | Presence flag for moderate 2050 scenario |
| `ext_2080` | Integer (0/1) | Presence flag for extreme 2080 scenario |
| `500yr` | Integer (0/1) | Presence flag for 500-year event |
| `mo_20_fldC` | String | DEP flood classification code for 2050 moderate scenario |
| `ex_20_fldC` | String | DEP flood classification code for 2080 extreme scenario |

---

## Additional Classifications

### Temporal Combinations

These fields can be calculated from the primary flags to analyze different flooding patterns:

| Field | Formula | Description |
|-------|---------|-------------|
| `past_present` | `BZ_past=1 AND BZ_present=1` | Blocks that flooded historically and currently flood |
| `present_future` | `BZ_present=1 AND BZ_future=1` | Blocks that currently flood and are predicted to flood |
| `past_future` | `BZ_past=1 AND BZ_future=1` | Blocks that flooded historically and are predicted to flood |
| `any_flooding` | `BZ_past=1 OR BZ_present=1 OR BZ_future=1` | Blocks with flooding in any time period |

---

## Field Naming Conventions

### Suffixes

| Suffix | Meaning | Example |
|--------|---------|---------|
| `A` | Area measurement in square feet | `beachesA` = area of beaches |
| `fg` | Flag indicating threshold met | `mod_cAfg` = flag for moderate current |
| `_sum` | Sum of multiple area measurements | `past_sum` = sum of all historical ecosystems |
| `C` | Classification or category code | `mo_cu_fldC` = flood classification |

### Prefixes

| Prefix | Meaning | Example |
|--------|---------|---------|
| `BZ_` | Blue Zone classification | `BZ_past`, `BZ_present`, `BZ_future` |
| `mod_` | Moderate flooding scenario | `mod_2050`, `mod_cA` |
| `ext_` | Extreme flooding scenario | `ext_2080` |




### Coordinate Reference System

- **EPSG Code**: 2263
- **Name**: NAD83 / New York Long Island (ftUS)
- **Units**: US Survey Feet
- **Suitable for**: New York City region analysis
- **Important**: All area measurements are in square feet


- **Royte & Sanderson (2026)**: Published methodology and findings

---

## Questions or Issues?

For questions about field definitions or data interpretation:
- Email: lroyte@nybg.org

*Last Updated: 2026*  
*Version: 1.0*
