states_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/54/query"

states_params = {
    "where" : "1=1",
    "outFields" : "NAME, STATE",
    "f" : "json"
}

'''
Example Response with Single Feature

{
 "displayFieldName": "BASENAME",
 "fieldAliases": {
  "NAME": "NAME"
 },
 "geometryType": "esriGeometryPolygon",
 "spatialReference": {
  "wkid": 102100,
  "latestWkid": 3857
 },
 "fields": [
  {
   "name": "NAME",
   "type": "esriFieldTypeString",
   "alias": "NAME",
   "length": 100
  }
 ],
 "features": [
  {
   "attributes": {
    "NAME": "Nevada",
    "STATE" : "32"
   },
   "geometry": {
    "rings": [
     [
      [
       -13283107.4022,
       5160069.1824000031
      ],
        ...
     ]
    ]
   }
  }
 ]
}
'''