import sqlite3
import centralities
import pickle
from sklearn import linear_model


class FlightNetworkInfo:


	def __init__(self):
		self.conn_ = sqlite3.connect('Flights.sqlite')
		self.cursor_ = self.conn_.cursor()
		self.ISOLATION_DATE = '2009-04-00'
		print "Initializing flight network"
		self.__calculateAvgDelaysByCarrier()
		print "Calculated avg delays by carrier"
		self.__calculateAvgDelaysByAirport()
		print "Calculated avg delays by airport"

	def LinearRegression(self):
		print "Beginning linear regression"
		self.__calculateLinearRegressionInput()
		print "Got linear regression input"
		coef = self.__executeLinearRegression()
		return coef

	def AvgDelaysByAirport(self):
		return (self.avgDepDelaysByAirport_, self.avgArrDelaysByAirport_)

	def AvgDelaysByCarrier(self):
		return (self.avgDepDelaysByCarrier_, self.avgArrDelaysByCarrier_)

	def __calculateAvgDelaysByCarrier(self):
		depDelayMap = {}
		arrDelayMap = {}
	
		self.cursor_.execute('select Carrier, avg(DepDelayMin), avg(ArrDelayMin) from Flight \
			where Cancelled = 0 and Diverted = 0 and FlightDate < ? group by Carrier', (self.ISOLATION_DATE, )) 
			# where FlightDate = ? group by Carrier', (isolationDate, ))
		delays = self.cursor_.fetchall()
		for carrier, depDelayMin, arrDelayMin in delays:
			depDelayMap[carrier] = depDelayMin
			arrDelayMap[carrier] = arrDelayMin

		self.avgDepDelaysByCarrier_ = depDelayMap
		self.avgArrDelaysByCarrier_ = arrDelayMap

		avgDepDelaysByCarrierFile = open('extra_data/avgDepDelaysByCarrier.pickle', 'w')
		avgArrDelaysByCarrierFile = open('extra_data/avgArrDelaysByCarrier.pickle', 'w')
		pickle.dump(depDelayMap, avgDepDelaysByCarrierFile)
		pickle.dump(arrDelayMap, avgArrDelaysByCarrierFile)

		return (depDelayMap, arrDelayMap)

	def __calculateAvgDelaysByAirport(self):
		depDelayMap = {}
		arrDelayMap = {}

		# isolationDate = '2009-03-04'

		self.cursor_.execute('select OriginAirportID, avg(DepDelayMin) from Flight \
			where Cancelled = 0 and Diverted = 0 and FlightDate < ? group by OriginAirportID', (self.ISOLATION_DATE, ))
		depDelays = self.cursor_.fetchall()
		for airport, depDelayMin in depDelays:
			depDelayMap[airport] = depDelayMin

		self.cursor_.execute('select DestAirportID, avg(ArrDelayMin) from Flight \
			where Cancelled = 0 and Diverted = 0 and FlightDate < ? group by DestAirportID', (self.ISOLATION_DATE, ))
		arrDelays = self.cursor_.fetchall()
		for airport, arrDelayMin in arrDelays:
			arrDelayMap[airport] = arrDelayMin

		self.avgDepDelaysByAirport_ = depDelayMap
		self.avgArrDelaysByAirport_ = arrDelayMap

		avgDepDelaysByAirportFile = open('extra_data/avgDepDelaysByAirport.pickle', 'w')
		avgArrDelaysByAirportFile = open('extra_data/avgArrDelaysByAirport.pickle', 'w')
		pickle.dump(depDelayMap, avgDepDelaysByAirportFile)
		pickle.dump(depDelayMap, avgArrDelaysByAirportFile)

		return (depDelayMap, arrDelayMap)

	# output features: 
	# CarrierDelay | WeatherDelay | NASDelay | SecurityDelay | LateAircraftDelay
	#
	# input features:
	# AirTime | Distance | ArrivalAirportInDegree | DepartureAirportOutDegree
	# CarrierAvgCarrierDelay | DepTimeofDay | ArrTimeofDay | 
	# DepAirportBetweennessCentrality | ArrAirportBetweennessCentrality

	def __calculateLinearRegressionInput(self):
		inputRows = []
		outputRows = []

		flightNetworkInfoByDate = {}

		# isolationDate = '2009-03-04'
		self.cursor_.execute('select OriginAirportID, DestAirportID, Carrier, FlightDate, AirTime, Distance, \
			DepTime, ArrTime, ArrDelayMin from Flight where Cancelled = 0 and Diverted = 0 and FlightDate < ?', (self.ISOLATION_DATE, ))
		for OriginAirportID, DestAirportID, Carrier, FlightDate, AirTime, Distance, DepTime, ArrTime, ArrDelayMin in self.cursor_.fetchall():

			if FlightDate not in flightNetworkInfoByDate:
				flightNetworkInfoByDate[FlightDate] = centralities.gen_node_info(FlightDate)
			flightNetworkInfo = flightNetworkInfoByDate[FlightDate]

			CarrierAvgDepDelay = self.avgDepDelaysByCarrier_[Carrier]
			CarrierAvgArrDelay = self.avgArrDelaysByCarrier_[Carrier]
			AirportAvgDepDelay = self.avgDepDelaysByAirport_[OriginAirportID]
			AirportAvgArrDelay = self.avgArrDelaysByAirport_[DestAirportID]

			if not CarrierAvgDepDelay:
				CarrierAvgDepDelay = 0.0
			if not CarrierAvgArrDelay:
				CarrierAvgArrDelay = 0.0
			if not AirportAvgDepDelay:
				AirportAvgDepDelay = 0.0
			if not AirportAvgArrDelay:
				AirportAvgArrDelay = 0.0

			OriginAirportInfo = flightNetworkInfo[OriginAirportID]
			DestAirportInfo = flightNetworkInfo[DestAirportID]

			OriginOutDeg = OriginAirportInfo[0]
			OriginInDeg = OriginAirportInfo[1]
			OriginBtwCentrality = OriginAirportInfo[2]
			OriginCloseCentrality = OriginAirportInfo[3]

			DestOutDeg = DestAirportInfo[0]
			DestInDeg = DestAirportInfo[1]
			DestBtwCentrality = DestAirportInfo[2]
			DestCloseCentrality = DestAirportInfo[3]

			# missing: AirTime, DepTime, ArrTime
			inputRow = (CarrierAvgDepDelay, CarrierAvgArrDelay, AirportAvgDepDelay, AirportAvgArrDelay, Distance, \
				OriginOutDeg, OriginInDeg, OriginBtwCentrality, OriginCloseCentrality, DestOutDeg, DestInDeg, DestBtwCentrality, \
				DestCloseCentrality)

			inputRows.append(inputRow)
			if ArrDelayMin is None:
				ArrDelayMin = 0
			outputRows.append(ArrDelayMin)

		self.linRegInputRows_ = inputRows
		self.linRegOutputRows_ = outputRows

		inputRowsFile = open('extra_data/inputRows.pickle', 'w')
		outputRowsFile = open('extra_data/outputRows.pickle', 'w')

		pickle.dump(inputRows, inputRowsFile)
		pickle.dump(outputRows, outputRowsFile)

		return inputRows, outputRows

	def __executeLinearRegression(self):
		clf = linear_model.LinearRegression()
		clf.fit(self.linRegInputRows_, self.linRegOutputRows_)

		linearRegressionPickleFile = open('extra_data/linear_regression_output.pickle', 'w')
		pickle.dump(clf.coef_, linearRegressionPickleFile)
		linearRegressionPickleFile.close()

		# linearRegressionFile = open('extra_data/linear_regression_output', 'w')
		# for coefficient in clf.coef_:
		# 	linearRegressionFile.write(str(coefficient))
		# linearRegressionFile.close()

		return clf.coef_
