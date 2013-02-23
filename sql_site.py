#!/usr/bin/python
# Rest Api and Front end for transforming SQL queries into persistent json responses
#
# @author Tim Hunter - tim@thunter.ca - @thorrsson
# 

from flask import Flask
from flask import request
from flask import render_template
from flask import url_for
from flask import json
from flask import jsonify
import socket 
import re

try:
	from pymongo import MongoClient
except ImportError:
	exit("ERROR: Could not import pymongo. Try easy_install pymongo")
	

app=Flask(__name__)
##	turn on debug
app.debug=True

##	set up our homepage route allows methods GET and POST, the first GET will render the input form, 
##	the POST will write the from contents to our MongoDB
@app.route('/', methods=['GET', 'POST'])
def home_page():
	##	layout our static files needed for the form pages
	url_for('static', filename='sql.css')
	url_for('static', filename='send_btn.png')
	url_for('static', filename='body_bg.png')

	##	if GET render or else: 
	if request.method == 'GET':
		return render_template('index.html', UserName='Username', Password='Password', ServerName="ServerName", DatabaseName='DatabaseName', query_hold='Query', fname_hold='FriendlyName')
	else:
		##	pull our data out of the from post values
		dbserver = request.form['serverName']
		dbuser= request.form['userName']
		dbpassword = request.form['password']
		dbname = request.form['DatabaseName']
		dbquery = request.form['sql']
		fname = request.form['fname']
		##	determine our hostname for use in our generated URL
		hostname = socket.gethostname()
		##	build our URL to pass back to the client
		url="http://%s:5000/" %(hostname) +request.form['fname'] 
		##	make sure we are only SELECT'ing ... TODO should also validate other inputs
		bad_regex=re.match("([iI]nsert|[uU]pdate|[dD]elete|[aA]lter)", dbquery)
		if bad_regex:
			print "you may only select data, no modifications are alowed"
			#return "You may only use SELECT statements, please go back and try again"
			return render_template('index.html', UserName=dbuser, ServerName=dbserver, Password='', DatabaseName=dbname, query_hold=dbquery, fname_hold=fname, sql_error='true')
		else:
		
			##	set up our mongoDB connection. Yes we assume localhost here
			mconnection = MongoClient('localhost', 27017)
			##	use the sqldb database
			mdb = mconnection.sqldb
			##	use the sql_collection collection in that DB
			mcollection = mdb.sql_collection
			##	build our nicely formated database insert
			mquery = {"serverName": dbserver,
				"userName": dbuser,
				"password": dbpassword,
				"DatabaseName": dbname,
				"sql": dbquery,
				"FriendlyName": fname}
			posts = mcollection
			##	let's check if a query named the same exists
			q_exists =  mcollection.find_one({'FriendlyName': fname})
			if q_exists:
				##	if it exists, currently we will update the query with the new values
				posts.update({'FriendlyName': fname}, mquery, upsert=True)
				print "Query named %s exists, updating" % fname
				##	render the results page
				return render_template('results.html', res_url=url);
			else:							
	
				##	put our insert results into a variable for logging
				post_id = posts.insert(mquery)
				##	TODO use real logging here right now we just console output the values
				print 'postid is: %s ' % post_id
				print 'inserted: %s ' % mquery
				##	render our results template with the URL filled in (page also renders a /<id> call in an iFrame to show the json results
				return render_template('results.html', res_url=url);

##	set up our calls for /<your FriendlyName> Allows GET for now ... TODO POST, PUT, DELETE
@app.route('/<id>', methods=['GET'])
def sql2json(id):
	item = id
	##	set up the MongoDB connection so we can pull the data out
	mconnection = MongoClient('localhost', 27017)
	mdb = mconnection.sqldb
	mcollection = mdb.sql_collection	
	##	we are keying on the /<id> being the FriendlyName (this URL is passed back to the user when they post their query the first time)
	##	TODO error handling, what if they pass an invalid ID, 
	##	TODO Logging too
	result = mcollection.find_one({'FriendlyName': item }) 		
	##	make sure we have a working mysqlDB
	try:
		import MySQLdb
	except ImportError:
		exit("ERROR: Could not import MySQLdb. Try: apt-get install python-mysqldb")
	##	Connection function, returns error if we can't connect
	def openDB(server,user,password,database):
		##      This function connects to the specified database. 
		dbcon = None
 		try:
			##  convert datetimes to strings
 			dbcon = MySQLdb.connect(server,user,password,database)
		except:
			print "ERROR: Could not connect to DB:", server
		return dbcon
	##	set our variables that are getting passed to the mysql server. Data comes from the mongo query we did based on ID
	dbserver = result[str('serverName')]
	dbuser= result[str('userName')]
	dbpassword = result[str('password')]
	dbname = result[str('DatabaseName')]
	dbquery = result[str('sql')]
	fname = result[str('FriendlyName')]
	##	open the connection and query
	connection = openDB(dbserver,dbuser,dbpassword,dbname)
	cursor = connection.cursor()
	##	execute the query or else pass back the error
	try:
		cursor.execute(dbquery)
		##	hacky hacky to get the column names into the dict that we are building with our results rows
		columns = tuple( [d[0].decode('utf8') for d in cursor.description] )
		q_result =[]
		for row in cursor:
			q_result.append(dict(zip(columns,[str(entry) if type(entry) not in (int,float,type(None),str,long) else entry for entry in row ])))
			#print [str(entry) for entry in row if type(entry) not in [int,float,None,str] or entry] 
	except MySQLdb.Error:
		return MySQLdb.Error
	##	clean up after ourselves
	connection.close()
	cursor.close()
	##	return a JSON blob as a result
	return jsonify({'results': list(q_result)})

if __name__ == '__main__':
	app.run(host='0.0.0.0')
