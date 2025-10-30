#!/usr/bin/env python3
"""
NRCS Data Client Demonstration

This script demonstrates the usage of the NRCSDataClient class for fetching soil data from
the NRCS Soil Data Access Web Service. It includes methods for fetching data via a GET
request that returns XML (with cleaning of stray ampersands and illegal control characters), and via a POST
request that sends a SQL query and returns JSON.
"""

import requests
import re
import textwrap
import xml.etree.ElementTree as ET


class NRCSDataClient:
    def __init__(self):
        # Initialize any configuration if needed
        pass

    def get_soil_map_unit(self, lat, lon):
        """
        Retrieves soil map unit data using a GET request which returns XML.
        Cleans the XML for stray ampersands and illegal control characters then parses it.
        Returns a list of dictionaries with keys: MUKEY, MUSYM, MUNAME.

        curl -X POST "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest" \
            --data "query=SELECT MUKEY FROM mapunit WHERE MUKEY IN (SELECT MUKEY from SDA_Get_Mukey_from_intersection_with_WktWgs84('POINT(-77.0 39.0)'))&format=json" \
            -H "Content-Type: application/x-www-form-urlencoded"

            {"Table":[["533592"]]}

        curl -X POST "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            --data "query=SELECT MUKEY, MUNAME, MUSYM, AsText(geom) as wkt_geom FROM mapunit WHERE MUKEY = 533592&format=json"

        curl -X POST "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            --data "query=SELECT MUKEY, MUNAME, MUSYM, AsText(geom) as wkt_geom FROM mapunit WHERE MUKEY = 533592&format=json"

            
        curl -X POST "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest" -H "Content-Type: application/x-www-form-urlencoded" --data "query=SELECT c.* FROM legend AS l JOIN mapunit AS m ON l.lkey = m.lkey JOIN component AS c ON m.mukey = c.mukey WHERE l.areasymbol = 'AZ649';&format=json"

        """
        url = f"https://sdmdataaccess.nrcs.usda.gov/Tabular/SoilWebService.asmx/GetSoilMapUnit?lat={lat}&lon={lon}"
        response = requests.get(url)
        response.raise_for_status()
        xml_str = response.text
        
        # Replace standalone ampersands with proper escape
        xml_str = re.sub(r'&(?!amp;|lt;|gt;|apos;|quot;)', '&amp;', xml_str)
        
        # Remove illegal XML control characters (characters in the range \x00-\x08, \x0B-\x0C, \x0E-\x1F)
        xml_str = re.sub("[\x00-\x08\x0B\x0C\x0E-\x1F]", "", xml_str)
        
        # Parse the XML data
        root = ET.fromstring(xml_str)
        units = []
        for mu in root.findall(".//MapUnit"):
            mukey = mu.find("MUKEY").text if mu.find("MUKEY") is not None else None
            musym = mu.find("MUSYM").text if mu.find("MUSYM") is not None else None
            muname = mu.find("MUNAME").text if mu.find("MUNAME") is not None else None
            units.append({
                "MUKEY": mukey,
                "MUSYM": musym,
                "MUNAME": muname
            })
        return units

    def get_mukey_by_coordinates(self, lat, lon):
        """
        Retrieves MUKEY data using a POST request with a SQL query. 
        The query checks if a point (given by lon, lat) is within the geometry of map units.
        The query is transformed into a single-line string.
        Returns the JSON response.
        """
        url = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"
        
        # Create a single-line SQL query (remove newlines, extra spaces)
        query = f"SELECT MUKEY FROM mapunit WHERE ST_Contains(geom, ST_PointFromText('POINT(-77.0 39.0)', 4326))"
        
        params = {
            "query": query,
        }
        
        response = requests.post(url, data=params)
        response.raise_for_status()
        return response.json()


def main():
    client = NRCSDataClient()
    lat, lon = 39.0, -77.0

    print("Fetching soil map unit data (XML)...")
    try:
        map_units = client.get_soil_map_unit(lat, lon)
        if map_units:
            print("Map units:")
            for unit in map_units:
                print(unit)
        else:
            print("No map unit data found.")
    except Exception as e:
        print("Error fetching soil map unit data:", e)

    print("\nFetching MUKEY data (JSON) with SQL query...")
    try:
        mukey_data = client.get_mukey_by_coordinates(lat, lon)
        print("MUKEY data:")
        print(mukey_data)
    except Exception as e:
        print("Error fetching MUKEY data:", e)


if __name__ == "__main__":
    main()
