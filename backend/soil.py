from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import geopandas as gpd
import shapely

app = FastAPI(title="Soil Data Access API", version="1.0.0")

# Allow all origins (for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SDM_URL = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"

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
