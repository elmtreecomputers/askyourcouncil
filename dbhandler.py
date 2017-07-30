import datetime
from tinydb import TinyDB, Query, where
import random

db = TinyDB('/home/pi/Projects/db.json')

#db.purge_tables() #everytime restart, just empty the tables

table = db.table('dht22')
table.purge()
timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
#table.insert({'temp': '10C', 'humidity':'10', 'timestamp':timestamp})

table2 = db.table('lmsensor')
table2.purge()
#timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
#table2.insert({'temp': '10C', 'timestamp':timestamp})


def insert_data(temp, humidity):
	db = TinyDB('/home/pi/Projects/db.json')

	timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
	table = db.table('dht22')

	table.insert({'temp': temp, 'humidity':humidity, 'timestamp':timestamp})
	
#	obj = table.search(where('temp')!="0 C")
	obj = table.all()
	count = len(obj)
	if(count>100):
		del_record('dht22')
	else:
		print("Retrieve last of ", count , " records")
		print(table.all())

def insert_data2(temp):
	db = TinyDB('/home/pi/Projects/db.json')
	timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
	table2 = db.table('lmsensor')
	table2.insert({'temp': temp, 'timestamp':timestamp})
#	obj = table2.search(where('temp')!="0 C")
	obj = table2.all()
	count = len(obj)
	if(count>100):
		del_record('lmsensor')
	else:
		retrieve_lmsensor()


def retrieve_data():
	db = TinyDB('/home/pi/Projects/db.json')
	table = db.table('dht22')
	data = []
	obj = table.all()
	count = len(obj)
	if(count>0):
		print("Retrieve last of ", count , " records")
		data = [obj[count-1]['temp'],obj[count-1]['humidity'],obj[count-1]['timestamp']]
		print(data)
	return data

def retrieve_data2():
	db = TinyDB('/home/pi/Projects/db.json')
	table2 = db.table('lmsensor')
	data = []
	obj = table2.all()
	count = len(obj)
	print("Retrieve last of ", count , " records")
	if(count>0):
		data = [obj[count-1]['temp'],obj[count-1]['timestamp']]
		print(data)
	return data

def retrieve_lmsensor():
#	db = TinyDB('/home/pi/Projects/db.json')
	table2 = db.table('lmsensor')
	table2.all()
	obj = table2.search(where('temp')!="0 C")
	count = len(obj)
	
	print("Retrieve LM sensor: ", count , " records")
        #data = [obj[count-1]['temp'],obj[count-1]['timestamp']]
	data = []
	
	sort_on = "timestamp"
	decorated = [(dict_[sort_on], dict_) for dict_ in obj]
	decorated.sort()
	result = [dict_ for (key, dict_) in decorated]

	for item in result:
		print(item , " " , item.eid)
		data.append(item)
	return data

def del_record(table_name):
	db = TinyDB('/home/pi/Projects/db.json')
	table = db.table(table_name)
	obj = table.all()
	#obj = table.search(where('temp')!="0 C")
	count = len(obj)
	if(count<1):
		return
        #data = [obj[count-1]['temp'],obj[count-1]['timestamp']]

	sort_on = "timestamp"
	decorated = [(dict_[sort_on], dict_) for dict_ in obj]
	decorated.sort()
	result = [dict_ for (key, dict_) in decorated]

	id_to_delete = []
	for item in result:
		print(item , " " , item.eid)
		id_to_delete.append(item.eid)
	print(id_to_delete)
	no_to_delete = len(result)-100
	if(no_to_delete>0):
		print("Deleting ", no_to_delete, " of ", count , " records of ", table_name)

		for i in range(0,no_to_delete):
			table.remove(eids=[id_to_delete[i]])


def retrieve_random_trivia():
	random_id = random.randint(1, 12)
	db = TinyDB('/home/pi/Projects/db.json')

	table = db.table('quotes')
	obj = table.search(where('id')==random_id)
	data = [obj[0]['content'],obj[0]['category']]
	print(data)
	return data


#del_record('dht22')
#del_record('lmsensor')



if __name__ == "__main__":
	table = db.table('dht22')
	table2 = db.table('lmsensor')
	table.purge()
	table2.purge()

