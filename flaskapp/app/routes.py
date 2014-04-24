from flask import Flask, render_template
from flask import stream_with_context, request, Response
from flask.ext.googlemaps import GoogleMaps
import os
import tablib
import csv

app = Flask(__name__)
GoogleMaps(app)
scholen = {}
#support csv reading
test = True


class UnicodeDictReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """
    param=None
    cut=None
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.encoding = encoding
        self.reader = csv.DictReader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        if self.param and self.cut:
        	if not (self.cut in row[self.param]):
        		# print row[self.param]
        		row = self.reader.next()
        #print row, '\n'
        return {k: unicode(v, "utf-8") for k, v in row.iteritems()}

    def __iter__(self):
        return self

def openFile(fileName, param=None, cut=None):
    try: 
        trainFile  = open(fileName, "rb")
    except IOError as e:
        print "File could not be opened: {}".format(e)
    else:
        reader = UnicodeDictReader(trainFile)
        reader.param = param #'type'
        reader.cut = cut #'Basisschool'
        return reader

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/the_map')
def the_map():
	datafile=openFile(os.path.join(os.path.dirname(__file__), 'static/data/onderwijsinstellingen_amsterdam_dmo-2.csv'))
	school ={}
	counter =0
	zoom = 9
	for row in datafile:
		# for key, value in row.iteritems():
		location = row['locatie'].replace('POINT(', '').replace(')', '').split(' ')
		school[row['titel']]=(float(location[1]), float(location[0]))
		counter+=1
	print counter
	return render_template('the_map.html', school=school, counter=counter, zoom=zoom)

@app.route('/the_map_basisschool')
def the_map_basisschool():
	datafile=openFile(os.path.join(os.path.dirname(__file__), 'static/data/onderwijsinstellingen_amsterdam_dmo-2.csv'), 
		param = 'type', cut = 'Basisschool')
	school ={}
	zoom = 11
	counter =0
	for row in datafile:
		# for key, value in row.iteritems():
		location = row['locatie'].replace('POINT(', '').replace(')', '').split(' ')
		school[row['titel']]=(float(location[1]), float(location[0]))
		counter+=1
	print counter
	return render_template('the_map.html', school=school, counter=counter, zoom=zoom)

@app.route('/the_map_basisschool_close')
def the_map_basisschool_close():
	my_location = {}
	my_location['lat'] = 52.363190
	my_location['long'] = 4.938290
	zoom=13
	datafile=openFile(os.path.join(os.path.dirname(__file__), 'static/data/onderwijsinstellingen_amsterdam_dmo-2.csv'), 
		param = 'type', cut = 'Basisschool')
	school ={}
	counter =0
	for row in datafile:
		# for key, value in row.iteritems():
		location = row['locatie'].replace('POINT(', '').replace(')', '').split(' ')
		distance = (my_location['long']-float(location[0]))**2+(my_location['lat']-float(location[1]))**2
		# #+ (location['long']-float(location[0])**2)
		if distance*1000 <0.1: 
			school[row['titel']]=(float(location[1]), float(location[0]))
			counter+=1
			print distance
	print counter
	return render_template('the_map.html', school=school, counter=counter, zoom=zoom)


@app.route('/the_table')
def the_table():
	datafile=openFile(os.path.join(os.path.dirname(__file__),'static/data/onderwijsinstellingen_amsterdam_dmo-2.csv'))
	return render_template('the_table.html', datafile=datafile)

@app.route('/the_table_basisschool_close')
def the_table_basisschool_close():
	my_location = {}
	my_location['lat'] = 52.363190
	my_location['long'] = 4.938290
	zoom=13
	datafile=openFile(os.path.join(os.path.dirname(__file__), 'static/data/onderwijsinstellingen_amsterdam_dmo-2.csv'), 
		param = 'type', cut = 'Basisschool')
	school ={}
	data_school = []
	counter =0
	for row in datafile:
		# for key, value in row.iteritems():
		location = row['locatie'].replace('POINT(', '').replace(')', '').split(' ')
		distance = (my_location['long']-float(location[0]))**2+(my_location['lat']-float(location[1]))**2
		# #+ (location['long']-float(location[0])**2)
		if distance*1000 <0.1: 
			school[row['titel']]=(float(location[1]), float(location[0]))
			counter+=1
			data_school.append(row['titel'])
	datafile=openFile(os.path.join(os.path.dirname(__file__), 'static/data/onderwijsinstellingen_amsterdam_dmo-2.csv'), 
		param = 'type', cut = 'Basisschool')
	return render_template('the_table_school.html', data_school=data_school, counter=counter, zoom=zoom, datafile=datafile)

 
if __name__ == '__main__':
  app.run(debug=True)