import sqlite3
import csv

def isNumeric(s):
	try:
		i = float(s)
		return True
	except ValueError, TypeErro:
		return False

conn = sqlite3.connect('Flights')

c = conn.cursor()

baseDirectory = '~/Downloads/'
baseString = 'On_Time_On_Time_Performance_'
insertString = "INSERT INTO Flight VALUES ("
nullPlaceHolder = "null"

for year in range(2012, 2013):
	for month in range(1,13):
		curFileName = baseString + str(year) + "_" + str(month)
		curPath = curFileName + "/" + curFileName + ".csv"
		print curPath

		with open(curPath, 'rU') as flights:
			flightsReader = csv.reader(flights)
			keys = [];
			i = 0
			for flight in flightsReader:
				if i == 0:
					for datum in flight:
						keys.append(datum)

				else:
					if i % 25000 == 0:
						print i
					index = 0
					insertCommand = insertString
					for datum in flight:
						if index < 69:
							if not isNumeric(datum):
								if datum == "":
									datum = nullPlaceHolder
								else:
									datum = '"' + datum + '"'
							insertCommand += datum
							index += 1
							if index < 69:
								insertCommand += ","
						else:
							break
					insertCommand += ")"
					#print insertCommand
					try:
						c.execute(insertCommand)
					except sqlite3.OperationalError:
						print insertCommand
						raise
				i += 1
			conn.commit()
conn.close()

