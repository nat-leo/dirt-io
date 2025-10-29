from fastapi import FastAPI, Query, HTTPException
import requests
import geopandas as gpd
import shapely

app = FastAPI(title="Soil Data Access API", version="1.0.0")

SDM_URL = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"

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

    return {"data": polygon}

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