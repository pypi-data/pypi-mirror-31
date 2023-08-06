# PYEMTAPI

Python library to access some functionality of the REST API of the Municipal Transport Company of Madrid.

You can see all the information about the API [here](http://opendata.emtmadrid.es/).

## Requirements
In order to attack the **EMT API** it is necessary to request credentials through the form [http://opendata.emtmadrid.es/Formulario](http://opendata.emtmadrid.es/Formulario). The keys arrive automatically, they do not do manual validation of the requests.

It is also necessary to have the following python library installed.

> urllib3 >= v1.22

## How to install
You can install the **py_emt** library by executing the following command.
>pip install pyemtapi

## How to use

**Import and authenticate against the API.**
```python
#!/usr/bin/python  
# -*- coding: utf-8 -*-
import pyemtapi
  
idClient = 'You idClient'  
passKey = 'You passKey'

api = pyemtapi.EMT(idClient, passKey)
```
**Finally, make the request by selecting a method.**
```python
# Returns a line/s route with the vertex info to build the route and coordinates for stops and axes  
print(api.GetRouteLines("04/05/2018", "26|27"))
```

> In the example.py file of this repository, you have an example with all the available methods.

**Response**

All the request will be of JSON type.


### Bus Methods 

|   Methods|Description |
| ---------|-------------|
| GetRouteLines| Returns a line/s route with the vertex info to build the route and coordinates for stops and axes |
| GetRouteLinesRoute| Get line route with vertex info to build map and coordinates for Stops |
| GetCalendar| Get EMT Calendar for all days and line schedules for a range of dates|
| GetListLines| Returns lines with description and groups     |
| GetListLinesExtend | Returns lines with description and groups with more information.|
| GetGroups| Returns every line type and their details |
| GetTimesLines| Returns current schedules for the requested lines|
| GetTimeTableLines| Provide information of the requested line with a trip-level detail.|
| GetNodesLines| Returns all stop identifiers and his coordinate, name, lines and directions|



### Geo Methods 

|   Methods|Description |
| ---------|-------------|
| GetStreet| Returns a list of EMT nodes related to a location. All EMT locations are a group of stops  within a target radius and the lines related to each stop in the list.|
| GetStopsFromStop| Returns a list of stops from a target stop with a target radius and the lines arriving to those stops.|
| GetStopsFromXY| Returns a list of stops from a coordinate with a radius and the lines arriving to those stops.|
| GetArriveStop| Gets bus arrive info to a target stop |
| GetPointsOfInterest| Returns a list of Points of Interest from a coordinate center with a target radius|
| GetPointsOfInterestTypes| Returns a list of Point of interest types|
| GetStreetFromXY| Returns a list of stops from a target coordinate.|
| GetInfoLine| Returns line info in a target date|
| GetInfoLineExtend| Returns line info in a target date with more information.|
| GetStopsLine| Provices information about the requested line at travel time.|
| GeoGetGroups| Return a list of groups |



