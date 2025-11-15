counties_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/55/query"


total_records_parms = {
    "where" : "1=1",
    "returnCountOnly" : "true",
    "f" : "json"
}

'''
Example Response for Total Records
{
    count : 3234
}
'''

counties_params = {
    "where" : "", #loop through total features based on OBJECTID with 1 indexing
    "outFields" : "NAME, STATE, POP100",
    "f" : "json"
}

'''
Example Response with Single Feature

{
 "displayFieldName": "NAME",
 "fieldAliases": {
  "NAME": "NAME",
  "STATE": "STATE",
  "POP100": "POP100"
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
  },
  {
   "name": "STATE",
   "type": "esriFieldTypeString",
   "alias": "STATE",
   "length": 2
  },
  {
   "name": "POP100",
   "type": "esriFieldTypeDouble",
   "alias": "POP100"
  }
 ],
 "features": [
  {
   "attributes": {
    "NAME": "Allen Parish",
    "STATE": "22",
    "POP100": 22750
   },
   "geometry": {
    "rings": [
     [
      [
       -10308029.890699999,
       3594670.498800002
      ],
      [
       -10308034.6775,
       3592380.2193000019
      ],
      ...
     ]
    ]
    }
    }
    ]
}
'''