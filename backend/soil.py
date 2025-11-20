
from __future__ import annotations

import requests
import geopandas as gpd
import shapely

from typing import Any, Dict, List, Set
import json
import math
import os
import re
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# --- FastAPI App --------------------------------------------------------------

app = FastAPI(title="Soil Data Access API", version="1.0.0")

# --- URLs ---------------------------------------------------------------------

AREA_SYMBOLS_PATH = os.getenv("AREA_SYMBOLS_PATH", "area-symbols.json")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

WFS_BASE_URL = "https://sdmdataaccess.sc.egov.usda.gov/Spatial/SDMWM.wfs"
SDM_URL = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"

# --- Config  ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:3000"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ------------------------------------------------------------

@app.get("/soil/sql", summary="Execute Arbitrary SQL Query on Soil Data Access API")
def execute_soil_sql(
    query: str = Query(..., description="SQL query to execute against the Soil Data Access API"),
):
    """
    Executes an arbitrary SQL query against the USDA Soil Data Access API.

    Example query:

    SELECT taxorder, taxsuborder, taxgrtgroup, taxsubgrp FROM component WHERE mukey = '459469' AND majcompflag = 'Yes'

    SELECT * WHERE areasymbol = 'CA635'

    SELECT mup.mupolygonkey, mup.mukey, mup.mupolygongeo FROM mupolygon AS mup WHERE mup.mukey IN (SELECT mukey FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('POINT(-122.449871 37.492633)'))

    SELECT 
        mu.mupolygonkey,
        mu.mukey,
        mu.mupolygongeo,
        c.compname,
        c.totcompd_r AS component_percent,
        c.taxorder,
        c.taxsuborder,
        c.taxgrtgroup,
        c.taxsubgrp,
        c.taxpartsize,
        c.taxtempcl,
        c.taxmoistcl,
        c.drainagecl,
        c.hydgrpdcd,
        c.rootdepth,
        ch.hzname,
        ch.hzdept_r,
        ch.hzdepb_r,
        ch.sandtotal_r,
        ch.silttotal_r,
        ch.claytotal_r,
        ch.dbthirdbar_r AS bulk_density,
        ch.ph1to1h2o_r AS ph,
        ch.ec_r AS salinity,
        ch.oc_r AS organic_carbon,
        ch.cec7_r AS cec,
        ch.sar_r AS sar,
        pm.pmkind,
        pm.pmorigin,
        pmgeom.geomdesc,
        pmgeom.geomfmod,
        ec.ecosysname,
        ec.ecoclasstypename
    FROM mu
    JOIN component AS c ON mu.mukey = c.mukey
    LEFT JOIN chorizon AS ch ON c.cokey = ch.cokey
    LEFT JOIN copm AS pm ON c.copmkey = pm.copmkey
    LEFT JOIN copmgrp AS pmgeom ON pm.copmgrpkey = pmgeom.copmgrpkey
    LEFT JOIN coecoclass AS ec ON c.cokey = ec.cokey
    WHERE mu.mukey = '459469' 
    ORDER BY mu.mupolygonkey, c.compname, ch.hzdept_r;
    
    Note: Use with caution. This endpoint allows execution of any SQL query.
    """

    payload = {"query": query, "format": "json"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(SDM_URL, data=payload, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")

    return data


@app.get("/soil", summary="Query Soil Map Units by Coordinates")
def get_soil_data(
    lon: float = Query(..., description="Longitude (WGS84)", ge=-180, le=180),
    lat: float = Query(..., description="Latitude (WGS84)", ge=-90, le=90),
):
    """
    Calls the USDA Soil Data Access API to get the map unit polygons
    that intersect with a given lon/lat point.

    Calling http://127.0.0.1:8000/soil?lon=-122.449871&lat=37.492633

    Will return a list of objects like this:
    data: [ [mupolygonkey, mukey, mupolygongeo], ... ]
    data: [

    ["399359807","456385","POLYGON ((-122.407560312536 37.4779244261786, -122.407733973112 37.4780814925273, 
    -122.407862057399 37.4781364448679, -122.408171588894 37.4781583629602, -122.408292518557 37.4786946355015, 
    -122.408352047996 37.4788057010266, -122.408529608099 37.479009220572, -122.408573768744 37.4791237129161, 
    -122.40856444971 37.4792510576282, -122.408503392026 37.4793602456609, -122.408413016505 37.4794574125652, 
    -122.408192443766 37.4796337157958, -122.407942253009 37.4797711550183, -122.407533347568 37.4799421248852, 
    -122.407256856097 37.4799944921145, -122.406561700487 37.4799926654537, -122.406181368536 37.4798157937298, 
    -122.406196852103 37.4793279801145, -122.406227498123 37.4792070163781, -122.406283858218 37.4790914543674, 
    -122.406375488664 37.4789977213531, -122.406619103595 37.4788422656638, -122.406697095187 37.4787404383286, 
    -122.406816784576 37.4783787816537, -122.406894930201 37.4782806312575, -122.407127405299 37.478130441184, 
    -122.407560312536 37.4779244261786))"],
    ...
    ]
    """

    query = f"""
    SELECT mup.mupolygonkey, mup.mukey, mup.mupolygongeo
    FROM mupolygon AS mup
    WHERE mup.mukey IN (
      SELECT mukey
      FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('POINT({lon} {lat})')
    )
    """

    payload = {"query": query, "format": "json"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(SDM_URL, data=payload, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")

    if "Table" not in data or not data["Table"]:
        return {"message": "No map unit polygons found for given coordinates"}
 
    polygon = find_polygon_with_coordinate(lat, lon, data["Table"])
    mukey = polygon[0][1] if polygon else None
    
    print("Fetched soil taxonomy for mukey:", mukey)
    print(f"{get_soil_info(mukey)}")

    return {"data": {
        "polygon": polygon,
        "soil_info": get_soil_info(mukey) if mukey else None}
    }

def find_polygon_with_coordinate(lat: float, lon: float, polygons: list) -> list:
    """
    Given a list of polygons (as WKT strings) and a lat/lon point,
    return the polygon that contains the point.
    This is a stub function; actual implementation would require
    a geometry library like Shapely to perform point-in-polygon tests.
    """
    point = shapely.Point(lon, lat)
    df = gpd.GeoDataFrame(
        polygons,
        columns=['mupolygonkey', 'mukey', 'wkt']
    )
    df['geometry'] = df['wkt'].apply(shapely.wkt.loads)
    df = df.drop(columns=['wkt'])

    # Assign CRS (WGS84)
    df = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    
    # Defensively, we're assuming there's still a chance of multiple matches
    matches = df[df.geometry.contains(point)]
    result = [ 
        [row['mupolygonkey'], row['mukey'], row['geometry'].wkt]
        for _, row in matches.iterrows()
    ]

    return result

def get_soil_info(mukey: str) -> dict:
    """
    Given a mukey, fetch soil characteristics from the Soil Data Access API.
    """
    query = f"""

    SELECT 
        c.mukey,
        c.taxorder as taxonomic_order,
        ecoclass.ecoclassname as ecological_class,
        STRING_AGG(species_name, ', ') AS dominant_species
    FROM component AS c

    -- Join ecological class
    JOIN coecoclass AS ecoclass ON c.cokey = ecoclass.cokey

    -- Combine all species tables into one union
    LEFT JOIN (
        SELECT cokey, plantcomname AS species_name FROM cocanopycover
        UNION
        SELECT cokey, plantcomname AS species_name FROM coforprod
        UNION
        SELECT cokey, plantcomname AS species_name FROM coeplants
    ) AS species_union
    ON c.cokey = species_union.cokey

    WHERE c.mukey = '{mukey}' AND c.majcompflag = 'Yes'
    GROUP BY c.mukey, c.taxorder, ecoclass.ecoclassname
    ORDER BY c.mukey;

    """
    # SELECT taxorder, taxsuborder, taxgrtgroup, taxsubgrp FROM component WHERE mukey = '{mukey}' AND majcompflag = 'Yes'

    payload = {"query": query, "format": "json"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(SDM_URL, data=payload, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        rows = data["Table"]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")

    return rows

@app.get("/map")
async def get_map(BBOX: str = Query(..., description="Bounding box as 'minLon,minLat,maxLon,maxLat' (like NRCS WFS)",),) -> Dict[str, Any]:
    """
    Return FeatureCollection<Polygon> for a bbox via SDMWM.wfs.

    BBOX format matches NRCS / WFS, e.g.:
      BBOX=-124.5,32.0,-113.0,42.0
    """

    # Parse BBOX string
    parts = [p.strip() for p in BBOX.split(",")]
    if len(parts) != 4:
        raise HTTPException(
            status_code=400,
            detail="BBOX must have 4 comma-separated numbers: minLon,minLat,maxLon,maxLat",
        )

    try:
        min_lon = float(parts[0])
        min_lat = float(parts[1])
        max_lon = float(parts[2])
        max_lat = float(parts[3])
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="BBOX values must be valid floats",
        )

    # Normalize + clamp (in case the user sends corners reversed)
    min_x = min(min_lon, max_lon)
    max_x = max(min_lon, max_lon)
    min_y = min(min_lat, max_lat)
    max_y = max(min_lat, max_lat)

    n_west = clamp_decimals(min_x)
    n_east = clamp_decimals(max_x)
    n_south = clamp_decimals(min_y)
    n_north = clamp_decimals(max_y)

    bbox_norm = f"{n_west},{n_south},{n_east},{n_north}"

    params = {
        "SERVICE": "wfs",
        "VERSION": "1.1.0",
        "REQUEST": "GetFeature",
        "TYPENAME": "surveyareapoly",
        "SRSNAME": "EPSG:4326",
        "BBOX": bbox_norm,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(WFS_BASE_URL, params=params)
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"WFS request failed: {e!s}")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"WFS responded with {resp.status_code}",
        )

    xml = resp.text
    feature_collection = parse_wfs_xml_to_feature_collection(xml)

    print(
        "[/map]",
        "BBOX=",
        BBOX,
        "normalized=",
        bbox_norm,
        "features=",
        len(feature_collection["features"]),
    )

    return feature_collection

# --- Helpers --------------------------------------------------------------------

def clamp_decimals(n: float, places: int = 12) -> float:
    """ NRCS Web Services require that the coordinates be
    12 decimal points or less.
    """
    return float(f"{n:.{places}f}")

def persist_area_symbols(symbols: Set[str]) -> None:
    """Keep a JSON file of unique area symbols grouped by State.

    Example file contents:
    {
      "CA": ["CA011", "CA689"],
      "AZ": ["AZ001", "AZ002"]
    }

    The goal is to eventually get all the area symbols and 
    mass download the data to storage so we can have parcel-level
    soil data - going way past county level we get from NRCS web 
    services.
    """
    if not symbols:
        return

    path = Path(AREA_SYMBOLS_PATH)
    existing: Dict[str, List[str]] = {}

    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except json.JSONDecodeError:
            existing = {}

    for symbol in symbols:
        if len(symbol) < 2:
            continue
        key = symbol[:2]
        bucket = existing.setdefault(key, [])
        if symbol not in bucket:
            bucket.append(symbol)
            bucket.sort()

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2))

# --- WFS XML Parsing -----------------------------------------------------------
coord_regex = re.compile(
    r'<gml:coordinates[^>]*>([^<]+)</gml:coordinates>', re.IGNORECASE
)

survey_area_regex = re.compile(
    r'<ms:surveyareapoly[^>]*fid="surveyareapoly\.([A-Z]{2}[0-9]{3})"[^>]*>([\s\S]*?)</ms:surveyareapoly>',
    re.IGNORECASE,
)

def parse_wfs_xml_to_feature_collection(xml: str) -> Dict[str, Any]:
    """Parse SDMWM.wfs XML into GeoJSON FeatureCollection<Polygon>."""

    features: List[Dict[str, Any]] = []
    discovered_symbols: Set[str] = set()

    for area_match in survey_area_regex.finditer(xml):
        area_symbol = area_match.group(1)
        area_content = area_match.group(2)

        if area_symbol:
            discovered_symbols.add(area_symbol)

        for coord_match in coord_regex.finditer(area_content):
            raw = coord_match.group(1).strip()

            points: List[List[float]] = []
            for pair in re.split(r"\s+", raw):
                nums = [p for p in re.split(r"[, ]+", pair) if p]
                if len(nums) != 2:
                    continue
                try:
                    a = float(nums[0])
                    b = float(nums[1])
                except ValueError:
                    continue
                if math.isnan(a) or math.isnan(b):
                    continue

                # Mirror your TS logic:
                #   .map(([lat, lng]) => [lng, lat])
                lat, lng = a, b
                points.append([lng, lat])

            if len(points) < 3:
                continue

            # Close polygon if not closed
            if points[0] != points[-1]:
                points.append(points[0])

            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [points],
                    },
                    "properties": {"areaSymbol": area_symbol} if area_symbol else {},
                }
            )

    if discovered_symbols:
        persist_area_symbols(discovered_symbols)

    return {
        "type": "FeatureCollection",
        "features": features,
    }