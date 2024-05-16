import requests
import db
import xml.etree.ElementTree as et

def get_trunc_coord(lat, long):
  truncated_lat = round(lat, 4)
  truncated_long = round(long, 4)
  return "{}, {}".format(truncated_lat, truncated_long)


def get_intersection(lat, long):
  k = get_trunc_coord(lat, long)
  
  local_is = db.query_coord(k)
  if local_is:
    print("[found locally] the intersection for coords {},{} is {}".format(lat, long, local_is[0]))
    return local_is[0]

  api_url = "http://api.geonames.org/findNearestIntersection?lat={}&lng={}&username=elleen".format(lat, long)
  response = requests.get(api_url)
  response_xml = et.fromstring(response.text)
  try:
    st1 = response_xml[0].find('street1').text
    st2 = response_xml[0].find('street2').text
    intersection = sorted([st1, st2])
    
    print("[geonames] the intersection for coords {},{} is {}".format(lat, long, intersection))
    intersection_str = "{}, {}".format(intersection[0], intersection[1])
    db.create_new_coord(k, intersection_str)
    return intersection_str
  
  except Exception as e:
    with open("err.txt", "a") as err:
      err.write("[geonames] failed to locate the intersection for {}, {}\n".format(lat, long))
    return

  
