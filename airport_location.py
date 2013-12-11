def read_in_airports():
  airports = {}
  with open('extra_data/locations.txt', 'r') as f:
    for line in f:
      data = line.split(', ')
      airports[int(data[0])] = (float(data[2]), float(data[1]))
  return airports

def get_lat_long(airport_code):
  airports = read_in_airports()
  if airport_code in airports.keys():
    return airports[airport_code]
  return None