from linear_regression import FlightNetworkInfo
import centralities
import sqlite3
import pickle
import heapq
import collections
import utc

class FlightPath:

	# each node contains: rowid, Carrier, FlightNum, OriginCityName, DestCityName, DepTime, ArrTime

	def __init__(self):
		self.startTime = 0
		self.endTime = 0
		self.flights = []

	def __cmp__(self, otherPath):
		return self.endTime - otherPath.endTime

	def addFlight(self, flight):
		flightEndTime = flight['ArrTime']
		assert(flightEndTime > self.endTime)
		self.endTime = flightEndTime
		self.flights.append(flight)

	def flights(self):
		return self.flights

	def totalFlightTime(self):
		return self.endTime - self.startTime

	def clone(self):
		clone = FlightPath()
		for flight in self.flights:
			clone.addFlight(flight)
		return clone

	def length(self):
		return len(self.flights)

	def lastFlight(self):
		return self.flights[self.length() - 1]

	def printPath(self):
		print 'Flight path:'
		for flight in self.flights:
			print 'Next flight: ', flight['Carrier'], ' flight ', flight['FlightNum']
			print 'Departure: ', utc.UTCToReadable(flight['DepTime'], str(flight['OriginAirportID'])), ' \
				from ', flight['OriginCityName'], ', OriginAirportID: ', flight['OriginAirportID']
			print 'Arrival: ', utc.UTCToReadable(flight['ArrTime'], str(flight['DestAirportID'])), ' \
				to ', flight['DestCityName'], ', DestAirportID: ', flight['DestAirportID']
		print 'End flight path'

class DelayPathfinder:

	def __init__(self, date, lin_reg_coef_filename):
		lin_reg_coef_file = open(lin_reg_coef_filename)
		self.coef_ = pickle.load(lin_reg_coef_file)
		self.date_ = date
		self.flight_graph_ = centralities.gen_daily(date)
		self.flight_network_info_ = FlightNetworkInfo()
		self.conn_ = sqlite3.connect('Flights.sqlite')
		self.cursor_ = self.conn_.cursor()

		depDelayMap, arrDelayMap = self.flight_network_info_.AvgDelaysByAirport()
		self.airportDepDelays_ = depDelayMap
		self.airportArrDelays_ = arrDelayMap
		depDelayMap, arrDelayMap = self.flight_network_info_.AvgDelaysByCarrier()
		self.carrierDepDelays_ = depDelayMap
		self.carrierArrDelays_ = arrDelayMap

		self.centralities_ = centralities.gen_node_info(date)

		ymd = self.date_.split('-')
		self.year_ = int(ymd[0])
		self.month_ = int(ymd[1])
		self.day_ = int(ymd[2])

		# print self.year_, " ", self.month_, " ", self.day_

		# print self.coef_

	def EstimatedDelay(self, flight):
		originNodeInfo = self.centralities_[flight['OriginAirportID']]
		destNodeInfo = self.centralities_[flight['DestAirportID']]
		inputRow = (self.carrierDepDelays_[flight['Carrier']], self.carrierArrDelays_[flight['Carrier']], \
			self.airportDepDelays_[flight['OriginAirportID']], self.airportArrDelays_[flight['DestAirportID']], \
			flight['Distance'], originNodeInfo[0], originNodeInfo[1], originNodeInfo[2], originNodeInfo[3], \
			destNodeInfo[0], destNodeInfo[1], destNodeInfo[2], destNodeInfo[3])
		
		expectedDelay = 0.0
		for i in range(len(inputRow)):
			expectedDelay += inputRow[i] * self.coef_[i]
		return expectedDelay

	def UTCTime(self, flightTime, airportID):
		hour = (flightTime / 100) % 24
		minute = flightTime % 100
		return utc.timeAndLocToUTC(self.year_, self.month_, self.day_, hour, minute, str(airportID))

	def AdjustTimeForEstimatedDelay(self, flight):

		depUTCTime = self.UTCTime(flight['DepTime'], flight['OriginAirportID'])
		arrUTCTime = self.UTCTime(flight['ArrTime'], flight['DestAirportID'])

		estimatedDelay = self.EstimatedDelay(flight)
		arrUTCTime += int(estimatedDelay * 60)

		if arrUTCTime < depUTCTime:
			# add a day
			arrUTCTime += 24 * 60 * 60

		flight['DepTime'] = depUTCTime
		flight['ArrTime'] = arrUTCTime

		# flightArrHour = flight['ArrTime'] / 100
		# flightArrMinute = flight['ArrTime'] % 100
		# flightArrMinute += estimatedDelay
		# hoursToAdd = flightArrMinute / 60
		# newArrTime = (flightArrHour + hoursToAdd) * 100 + (flightArrMinute % 60)
		# flight['ArrTime'] = newArrTime
		return flight

	def BFS(self, sourceAirportID, finalAirportID, startTime):
		flightPathQueue = []
		visitedCities = collections.defaultdict(lambda: 0)
		takenFlights = collections.defaultdict(lambda: 0)
		visitedCities[sourceAirportID] = 1

		if sourceAirportID == finalAirportID:
			return

		self.cursor_.execute('select rowid, OriginAirportID, DestAirportID, Carrier, FlightNum, \
			OriginCityName, DestCityName, DepTime, ArrTime, Distance from Flight \
			where OriginAirportID = ? and DepTime >= ? and FlightDate = ? \
			and Cancelled = 0 and Diverted = 0', (sourceAirportID, startTime, self.date_))
		for rowid, OriginAirportID, DestAirportID, Carrier, FlightNum, \
			OriginCityName, DestCityName, DepTime, ArrTime, Distance in self.cursor_.fetchall():

			nextFlightPath = FlightPath()
			nextFlight = {'rowid': rowid, 'OriginAirportID': OriginAirportID, 'DestAirportID': DestAirportID, 'Carrier': Carrier, \
				'FlightNum': FlightNum, 'OriginCityName': OriginCityName, 'DestCityName': DestCityName, 'DepTime': DepTime, \
				'ArrTime': ArrTime, 'Distance': Distance}
			
			nextFlight = self.AdjustTimeForEstimatedDelay(nextFlight)
			nextFlightPath.addFlight(nextFlight)

			heapq.heappush(flightPathQueue, nextFlightPath)
			visitedCities[DestAirportID] = 1
			takenFlights[rowid] = 1

		while len(flightPathQueue) != 0:
			nextFlightPath = heapq.heappop(flightPathQueue)
			lastFlight = nextFlightPath.lastFlight()

			# print 'exploring'
			# nextFlightPath.printPath()

			if lastFlight['DestAirportID'] == finalAirportID:
				# reached destination, bitch
				return nextFlightPath
			visitedCities[lastFlight['DestAirportID']] = 1

			self.cursor_.execute('select rowid, OriginAirportID, DestAirportID, Carrier, FlightNum, \
				OriginCityName, DestCityName, DepTime, ArrTime, Distance from Flight \
				where OriginAirportID = ? and FlightDate = ? and Cancelled = 0 and Diverted = 0', \
				(lastFlight['DestAirportID'], self.date_))


			for rowid, OriginAirportID, DestAirportID, Carrier, FlightNum, \
				OriginCityName, DestCityName, DepTime, ArrTime, Distance in self.cursor_.fetchall():

				if DestAirportID in visitedCities:
					continue
				if rowid in takenFlights:
					continue

				nextFlight = {'rowid': rowid, 'OriginAirportID': OriginAirportID, 'DestAirportID': DestAirportID, 'Carrier': Carrier, \
					'FlightNum': FlightNum, 'OriginCityName': OriginCityName, 'DestCityName': DestCityName, 'DepTime': DepTime, \
					'ArrTime': ArrTime, 'Distance': Distance}
				nextFlight = self.AdjustTimeForEstimatedDelay(nextFlight)

				if nextFlight['DepTime'] < lastFlight['ArrTime']:
					continue

				flightPathClone = nextFlightPath.clone()
				flightPathClone.addFlight(nextFlight)
				# print 'evaluated to path: '
				# flightPathClone.printPath()

				takenFlights[rowid] = 1
				heapq.heappush(flightPathQueue, flightPathClone)

		return None
