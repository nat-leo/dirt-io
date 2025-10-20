# Working with Soil
SSURGO data, especially from the NRCS, is a treasure trove of information about the soils of the United States. There's entire 
manuals on the collection of good data for this project. 

This project contains an example dataset downloaded from the NRCS Web Soil Survey tool in the folder `Working with Soil/AZ649`

Soil Survey Staff, Natural Resources Conservation Service, United States Department of Agriculture. Web Soil Survey. Available online at the following link: http://websoilsurvey.sc.egov.usda.gov/. Accessed [10/19/2025].

## Getting Started
This is a large, complex geospatial dataset. It's split into `spatial` and `tabular` services. `spatial` data gives map polygons that 
can be viewed on GIS tools. `tabular` data gives detailed information on the soil characteristics of each zone. We connect spatial and
tabular data together by key - the `mapunit`.

Access tabular data, like soil horizons, compositions, slopes, water, and mineral content from `https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest`
```
curl -X POST "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest" -H "Content-Type: application/x-www-form-urlencoded" --data "query=<PUT YOUR SQL HERE!>&format=json"
```

## Data Format

Once the mapunit key is known, tables can be accessed by that key. They just have different names within each table. Here's a few of the available tables 
and the name of their mapunit key. 

| Table                        | Description                                | Key       |
| ---------------------------- | ------------------------------------------ | --------- |
| `legend`                     | Survey area metadata (one per map legend)  | `lkey`    |
| `mapunit`                    | Soil map units (polygons on the map)       | `mukey`   |
| `component`                  | Soil components within each map unit       | `cokey`   |
| `chorizon`                   | Horizons (layers) within each component    | `chkey`   |
| `chtexturegrp` / `chtexture` | Texture groups & details                   | `chtgkey` |
| `cointerp` / `muinterp`      | Interpretations (e.g. suitability ratings) | `coiid`   |
| `muaggatt`                   | Aggregated soil attributes per map unit    | `mukey`   |

## But how do I find a mapunit?

Coordinates can be used to find map units as well.

```
curl -X POST "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest" \
            --data "query=SELECT MUKEY FROM mapunit WHERE MUKEY IN (SELECT MUKEY from SDA_Get_Mukey_from_intersection_with_WktWgs84('POINT(<LONGITUDE> <LATITUDE>)'))&format=json" \
            -H "Content-Type: application/x-www-form-urlencoded"
```
```
{"Table":[["533592"]]}
```