import sqlite3
import networkx as nx

'''
NOTE: the graph is structured as follows:
  NODE_ID: airport code
  EDGE_ID: unique flight identifier
  EDGE_WEIGHT: time of flight (in minutes)
'''

# Read in database
_db = sqlite3.connect('Flights.sqlite')
_c = _db.cursor()

def gen_daily(takeoff_date):

  # Initializing variables
  attributes = 'rowid, FlightDate, OriginAirportID, DestAirportID, CRSElapsedTime'
  FLIGHT_ID = 0
  FLIGHT_DATE = 1
  SOURCE_AIRPORT = 2
  DESTINATION_AIRORT = 3
  FLIGHT_TIME = 4

  # Query the database
  date = (takeoff_date,)
  _c.execute('select ' + attributes + ' from Flight where FlightDate=?', date)

  # Construct the graph
  daily_flights = nx.MultiDiGraph()

  for flight in _c.fetchall():
    src = flight[SOURCE_AIRPORT]
    dst = flight[DESTINATION_AIRORT]
    uid = flight[FLIGHT_ID]
    time = flight[FLIGHT_TIME]
    daily_flights.add_edge(src, dst, key=uid, duration=time)
  
  return daily_flights

# Returns a map with the following structure:
# { AirportID => (in-deg, out-deg, betw-cent, clos-cent) }
def gen_node_info(date, pre_computed_graph=None):
  node_info = {}
  daily_graph = None
  if pre_computed_graph is None:
    daily_graph = gen_daily(date)
  else:
    daily_graph = pre_computed_graph
  betw_cents = nx.betweenness_centrality(daily_graph, weight='duration')
  clos_cents = nx.closeness_centrality(daily_graph, distance='duration')
  for node in daily_graph.nodes():
    indeg = daily_graph.in_degree(node)
    outdeg = daily_graph.out_degree(node)
    node_info[node] = (indeg, outdeg, betw_cents[node], clos_cents[node])
  return node_info