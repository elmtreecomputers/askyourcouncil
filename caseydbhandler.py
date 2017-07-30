import pygeoj
from geopy.distance import vincenty
from decimal import Decimal

from operator import itemgetter


testfile = pygeoj.load(filepath="datasets/mchlocations.geojson")

home_lat = -38.01
home_long = 145.30

def closestChildCare(home_lat, home_long):

 childcareList = []
 for feature in testfile:
 	childcare ={}
 	print(feature.properties['name'])
 	childcare['name']=feature.properties['name']
 	print(feature.properties['address'])
 	childcare['address']=feature.properties['address']
 	childcare['telephone']=feature.properties['telephone_no']
 	print(feature.geometry.coordinates)
 	lat = feature.geometry.coordinates[1]
 	long = feature.geometry.coordinates[0]
 	target_loc = (lat,long)
 	home_loc = (home_lat, home_long)
 	distance = Decimal(vincenty(home_loc, target_loc).meters/1000)
 	distance = str(round(distance,2))
 	childcare['distance']=distance

 	print("Distance: " , str(distance) , " km")
 	print("--------------------------\n")
 	childcareList.append(childcare)
 childcareList.sort(key=itemgetter('distance'))

 no = 1
 for i in range(0,3):
 	print(no)
 	print(childcareList[i])
 	print("-------")
 	no+=1
 return childcareList

if __name__=="__main__":
 closestChildCare(home_lat, home_long)
