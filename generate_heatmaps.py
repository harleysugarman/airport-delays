import heatmap
import simplekml
import networkx as nx
import pickle
from math import log
import centralities as c

heatmap_scale = 10

def read_in_airports():
  airports = {}
  with open('extra_data/locations.txt', 'r') as f:
    for line in f:
      data = line.split(', ')
      airports[int(data[0])] = (float(data[2]), float(data[1]))
  return airports

def read_in_delays():
  arr_delays = {}
  dep_delays = {}
  with open('extra_data/avgArrDelaysByAirport.pickle', 'rb') as f:
    arr_delays = pickle.load(f)
  with open('extra_data/avgDepDelaysByAirport.pickle', 'rb') as f:
    dep_delays = pickle.load(f)
  return arr_delays, dep_delays

def calculate_normalised_delays(arr_delays, dep_delays):
  avg_delays = {}
  for key in arr_delays.keys():
    avg_delays[key] = float(arr_delays[key]+dep_delays[key])/2
  return avg_delays

def generate_delay_heatmap_points(airports, avg_delays):
  pts = []
  max_delay = max(round(x) for x in avg_delays.values())
  for key, val in airports.iteritems():
    if key in avg_delays.keys():
      delay = int(round(avg_delays[key]))
      normalized_delay = int(heatmap_scale*float(delay)/max_delay)
      for i in range(normalized_delay):
        pts.append(val)
    else:
      pts.append(val)
  return pts

def generate_delay_over_degree(airports, avg_delays, airport_info):
  pts = []
  log_degs = [log(int(v[0]) + int(v[1])) for k, v in  airport_info.items()]
  max_delay = max([v for k, v in avg_delays.iteritems()])
  min_log_deg = min([x for x in log_degs])
  max_del_deg = float(max_delay)/min_log_deg
  for key, val in airports.iteritems():
    if key in avg_delays.keys() and key in airport_info.keys():
      log_degree = log(int(airport_info[key][0])+int(airport_info[key][1]))
      delay = int(round(avg_delays[key]))
      del_deg = float(delay)/log_degree
      normalized_del_deg = int(heatmap_scale*float(del_deg)/max_del_deg) + 1
      for i in range(normalized_del_deg):
        pts.append(val)
    else:
      pts.append(val)
  return pts

def generate_delay_times_betw_centrality(airports, avg_delays, airport_info):
  pts = []
  bcs = [float(x[2]) for x in airport_info.values()]
  max_delay = max([v for k, v in avg_delays.iteritems()])
  max_bc = max(x for x in bcs)
  max_del_bc = float(max_delay)*max_bc
  for key, val in airports.iteritems():
    if key in avg_delays.keys() and key in airport_info.keys():
      bc = float(airport_info[key][2])
      delay = int(round(avg_delays[key]))
      del_bc = float(delay)*bc
      normalized_del_bc = int(heatmap_scale*float(del_bc)/max_del_bc) + 1
      for i in range(normalized_del_bc):
        pts.append(val)
    else:
      pts.append(val)
  return pts

def generate_degree_heatmap_points(airports, airport_info):
  pts = []
  log_degs = [log(int(v[0]) + int(v[1])) for k, v in  airport_info.items()]
  max_log_deg = max(x for x in log_degs)
  for key, val in airports.iteritems():
    if key in airport_info.keys():
      log_deg = log(int(airport_info[key][0])+int(airport_info[key][1]))
      normalized_log_deg = int(heatmap_scale*float(log_deg)/max_log_deg) + 1
      for i in range(normalized_log_deg):
        pts.append(val)
    else:
      pts.append(val)
  return pts

airports = read_in_airports()
daily_flights = c.gen_daily('2010-12-23')
airport_info = c.gen_node_info('2010-12-23', daily_flights)
arr_delays, dep_delays = read_in_delays()
avg_delays = calculate_normalised_delays(arr_delays, dep_delays)

del_pts = generate_delay_heatmap_points(airports, avg_delays)
deg_pts = generate_degree_heatmap_points(airports, airport_info)
del_deg_pts = generate_delay_over_degree(airports, avg_delays, airport_info)
del_bc_pts = generate_delay_times_betw_centrality(airports, avg_delays, airport_info)


kml = simplekml.Kml()
for airport in daily_flights.nodes():
  for neighbor in nx.all_neighbors(daily_flights, airport):
    flightpath = (airports[airport], airports[neighbor])
    path = kml.newlinestring(name='flightpath', coords=flightpath)
kml.save("KMLs/air_travel_network.kml")
print("Generated Air Travel Network")


del_hm = heatmap.Heatmap()
del_hm.heatmap(del_pts, dotsize=15, opacity=200, area=((-180, 15), (145, 75))).save("KMLs/heatmap_avg_delay.png")
print("Generated Heatmap for Average Delay")

deg_hm = heatmap.Heatmap()
deg_hm.heatmap(deg_pts, dotsize=15, opacity=200, area=((-180, 15), (145, 75))).save("KMLs/heatmap_degree.png")
print("Generated Heatmap for Airport Degree")

del_deg_hm = heatmap.Heatmap()
del_deg_hm.heatmap(del_deg_pts, dotsize=15, opacity=200, area=((-180, 15), (145, 75))).save("KMLs/heatmap_delay_over_degree.png")
print("Generated Heatmap for Delay Over Log(Degree)")

del_bc_hm = heatmap.Heatmap()
del_bc_hm.heatmap(del_bc_pts, dotsize=15, opacity=200, area=((-180, 15), (145, 75))).save("KMLs/heatmap_delay_times_bc.png")
print("Generated Heatmap for Delay Times Betweenness Centrality")