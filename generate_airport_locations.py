import sqlite3
from lxml import html

# Read in database
_db = sqlite3.connect('Flights.sqlite')
_c = _db.cursor()

# Generates a map of airports/locations
# Warning - DO NOT RUN THIS FUNCTION WITHOUT FIRST CHECKING WITH HARLEY!
# This takes a long time to run and fails on some airports because of
# the inconsistencies in the webpages being crawled. A finished list of airport
# locations is in the Dropbox.
def gen_map(takeoff_date):

  date = (takeoff_date,)
  airport_map = {}
  src_map = set(_c.execute('select Origin, OriginAirportID from Flight where FlightDate=?', date))
  dst_map = set(_c.execute('select Dest, DestAirportID from Flight where FlightDate=?', date))
  src_map.update(dst_map)
  for airport in src_map:
    airport_code = airport[0]

    # example url for LAX airport: http://www.airnav.com/airport/LAX
    url = 'http://www.airnav.com/airport/' + airport_code

    # the xpath to the longitude and latitude information on the page
    xpath = '/html/body/table[5]/tr/td[1]/table[1]/tr[2]/td[2]/text()[3]'

    print "Scanning URL: " + url

    html_tree = html.parse(url).getroot()
    coord_str = html_tree.xpath(xpath)[0]
    coords = coord_str.split(" / ")

    airport_map[airport[1]] = (float(coords[0]), float(coords[1]))

  return airport_map