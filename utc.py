from datetime import datetime, timedelta
from pytz import timezone
import calendar
import pytz

airportIDsFile = open('extra_data/airport_codes.txt')
airportIDsToTimeZone = {}
for line in airportIDsFile:
	tokens = line.split(" : ")
	airportID = tokens[0]
	timeZone = tokens[1][:-1]
	airportIDsToTimeZone[airportID] = timeZone

def timeAndLocToUTC(year, month, day, hours, minutes, airportID):
	if airportID not in airportIDsToTimeZone:
		return -1
	timeZone = int(airportIDsToTimeZone[airportID])
	timeString = "%d-%d-%d %2d:%2d:00" % (year, month, day, hours, minutes)
	naive = datetime(year, month, day, hours, minutes, 0)
	print naive
	naive = naive + timedelta(hours=(-1 * timeZone))
	seconds = (naive - datetime(1970,1,1)).total_seconds()
	return seconds

def UTCToReadable(seconds, airportID):
	timeZone = int(airportIDsToTimeZone[airportID])
	print timeZone
	seconds += ((timeZone + 8) * 60 * 60)
	readable = datetime.fromtimestamp(seconds)
	print readable
	return str(readable.date()) + " " + str(readable.time())

#print timeAndLocToUTC(2012, 2, 3, 6, 3, )
