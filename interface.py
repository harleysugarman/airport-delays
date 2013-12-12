#!/usr/bin/env python
import cli.app
import quickest_path

@cli.app.CommandLineApp
def ls(app):
	dateString = "%d-%s-%s" % (app.params.year, str(app.params.month).zfill(2), str(app.params.day).zfill(2))
	earliestTimeString = "%d" % app.params.earliestTime
	# print dateString
	# print earliestTimeString
	pathfinder = quickest_path.DelayPathfinder(dateString, 'extra_data/linear_regression_output.pickle')
	path = pathfinder.BFS(app.params.source, app.params.destination, earliestTimeString)
	print "FINAL PATH"
	path.printPath()

ls.add_param("source", help="source airport", default=0, type=int)
ls.add_param("destination", help="destination airport", default=0, type=int)
ls.add_param("year", help="year of departure", default=2013, type=int)
ls.add_param("month", help="month of departure", default=1, type=int)
ls.add_param("day", help="day of departure", default=1, type=int)
ls.add_param("earliestTime", help="earliest time of departure", default=0, type=int)

if __name__ == "__main__":
    ls.run()
