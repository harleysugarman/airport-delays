airport-delays
==============

A simulation of the US air traffic network with a shortest-path finder for flights (based on linear regression and Dijkstra's algorithm), and a KML heat map generator.

## Notes

- To operate this code, you will need to download the SQLite database of flights we prepared (approximately 7GB in size). Due to size limitations, this is not currently stored online for public download. If the status of this changes, we will update this README with its location.

## Example Outputs

- Input: SBA -> JFK on 03-03-2009

Next flight:  OO  flight  5510
Departure:  -8
2009-03-03 22:03:00         from  Santa Barbara, CA , OriginAirportID:  14689
Arrival:  -8
2009-03-03 23:05:53         to  Los Angeles, CA , DestAirportID:  12892

Next flight:  AA  flight  118
Departure:  -8
2009-03-03 23:37:00         from  Los Angeles, CA , OriginAirportID:  12892
Arrival:  -5
2009-03-04 07:50:42         to  New York, NY , DestAirportID:  12478

## Useful Information
Flight Database Schema:
CREATE TABLE FlightTest(RowID integer primary key asc, Year integer, Quarter integer, Month integer, DayofMonth integer, DayofWeek integer, FlightDate text, UniqueCarrier text, AirlineID integer, Carrier text, TailNum integer, FlightNum integer, OriginAirportID integer, OriginAirportSeqID integer, OriginCityMarketID integer, Origin text, OriginCityName text, OriginState text, OriginStateFips integer, OriginStateName text, OriginWac integer, DestAirportID integer, DestAirportSeqID integer, DestCityMarketID integer, Dest text, DestCityName text, DestState text, DestStateFips text, DestStateName text, DestWac text, CRSDepTime integer, DepTime integer, DepDelay integer, DepDelayMin integer, DepDel15 integer, DepartureDelayGroups integer, DepTimeBlk text, TaxiOut integer, WheelsOff integer, WheelsOn integer, TaxiIn integer, CRSArrTime integer, ArrTime integer, ArrDelay integer, ArrDelayMin integer, ArrDel15 integer, ArrivalDelayGroup integer, ArrTimeBlk integer, Cancelled integer, CancellationCode text, Diverted integer, CRSElapsedTime integer, ActualElapsedTime integer, AirTime integer, Flights integer, Distance integer, DistanceGroup integer, CarrierDelay integer, WeatherDelay integer, NASDelay integer, SecurityDelay integer, LateAircraftDelay integer, FirstDepTime integer, TotalAddGTime integer, LongestAddGTime integer, DivAirportLandings integer, DivReachedDest integer, DivActualElapsedTime integer, DivArrDelay integer, DivDistance integer);
