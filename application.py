from flask import Flask, request, session, jsonify
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_session import Session
from convsha import encryptstring
from distcal import calculatedist
from PIL import Image
#import Image
import io
import flask
import werkzeug

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app) 

database_url = "postgres://craftqywjmojeg:720ba0e8ddd25d680225570b31e65dc6ccfb636b057b9d6bb0e95cfba55cc38d@ec2-34-224-229-81.compute-1.amazonaws.com:5432/dddeh3aesqdhpf"

engine = create_engine(database_url)
db = scoped_session(sessionmaker(bind = engine))



@app.route("/user/login", methods = ['GET','POST']) # java local server route : "login"
def uloginfunc():
	msg = request.form.get('name')
	msgjson = json.loads(msg)

	username = msgjson['username']
	password = msgjson['password']
	
	print("device trying to login")

	data = db.execute("SELECT * FROM logincreden where phoneno = :tusername and passwd = :tpassword ",
		{"tusername" : username, "tpassword" : password}).fetchall()

	
	if len(data) > 0 :
		session['username'] = username
		print("success")
		return jsonify(status = "success", username = session.get('username') )

	else :
		print("fail")
		return jsonify(status = "fail", reason = "wrong username or password")

@app.route("/user/signup", methods=["GET","POST"]) # java local server route : "signup"
def usignupfunc():

	# start get data
	msg = request.form.get('name')
	msgjson = json.loads(msg)
	# end
	name = msgjson['username']
	phoneno = msgjson['phoneno']
	password = msgjson['password']
	status = "default"
	print("device user trying to signup")

	data = db.execute("SELECT * FROM logincreden where phoneno = :tusername", 
		{"tusername" : phoneno }).fetchall()
	if len(data) > 0:
		status = "user already exist"
	else :
		db.execute("INSERT INTO logincreden values ( :tname, :tphoneno, :tpasswd)", 
		{"tname": name, "tphoneno" : phoneno, "tpasswd": password})
		db.commit()
		status = "success"
	
	return jsonify(status = status )

# remaining!!
@app.route("/police/login", methods=['GET', 'POST']) # java local server route : "plogin"
def plogin():
	msg = request.form.get('name')
	msgjson = json.loads(msg)

	username = msgjson['username']
	password = msgjson['password']

	print("device police trying to login")

	data = db.execute("SELECT * FROM policecreden where phoneno = :tusername and passwd = :tpassword ",
		{"tusername" : username, "tpassword" : password}).fetchall()
	if len(data) > 0 :
		session['pusername'] = username
		return jsonify(status = "success", username = session.get('username') , policeid = data[0][0])

	else :
		return jsonify(status = "success", reason = "wrong username or password" )

# remaining!!
@app.route("/police/signup", methods=['POST', 'GET']) # java local server route : "psignup"
def psignupfunc():

	# start get data
	msg = request.form.get('name')
	msgjson = json.loads(msg)
	# end
	name = msgjson['username']
	phoneno = msgjson['phoneno']
	password = msgjson['password']
	status = "default"
	print("device trying to signup")

	data = db.execute("SELECT * FROM policecreden where phoneno = :tusername", 
		{"tusername" : phoneno }).fetchall()
	if len(data) > 0:
		status = "user already exist"
	else:
		db.execute("INSERT INTO policecreden (name1 ,phoneno, passwd) values ( :tname, :tphoneno, :tpasswd)", 
		{"tname": name, "tphoneno" : phoneno, "tpasswd": password})
		db.commit()
		status = "success"

		print("success")
	
	return jsonify(status = status)



@app.route("/police/location") # java local server route : "location"
def plocationfunc():
	# start get data 
	
	# end
	latitude = "sample"
	longitude = "sample"
	policeid = "1"

	db.execute("insert into policelocation values(:tpoliceid, :tlatitude, :tlongitude , '1')", 
		{"tpoliceid": policeid, "tlatitude" : latitude, "tlongitude" :longitude})
	db.commit()

	return "none"

@app.route("/user/recimage", methods=['GET', 'POST']) # java local server route : "image"
def recimagefunc():
	# start get data 
	imagefile = flask.request.files['image']
	filename = werkzeug.utils.secure_filename(imagefile.filename)

	print("\nReceived image File name : " + imagefile.filename)
	imagefile.save(filename)
	return "Image Uploaded Successfully"



@app.route("/user/coordinatedata", methods=['GET', 'POST']) # java local server route : "coordinate"
def ucoordinate():
	# start get data 
	msg = request.form.get('name')
	msgjson = json.loads(msg)
	# end

	latitude = msgjson['latitude']
	longitude = msgjson['longitude']
	desc_type = msgjson['casetype']
	desc_data = msgjson['description']

	# start get name of user from username from database
	nameuser = msgjson['username']
	# end

	# start calculate distance from nearest police
	policeloc = db.execute("select * from policelocation ").fetchall()
	policelist = []
	for pdata in policeloc:
		distance = calculatedist('19.912545', '77.577991', pdata[1], pdata[2])
		policelist.append([pdata[0], distance])


	tempdist = policelist[0][1]
	temppid = policelist[0][0]
	for ele in range(len(policelist)):
		if (tempdist > policelist[ele][1]):
			tempdist = policelist[ele][1]
			temppid = policelist[ele][0]

	nearestpolice = temppid
	nearestpolice = 1
	# end

	db.execute("INSERT INTO casedetail( pid, latitude, longitude, victimname, casetype, description) values( :tpid, :tlatitude, :tlongitude, :tnameuser, :tcasetype, :tdesc)", 
		{ "tpid" : nearestpolice, "tlatitude" : latitude, "tlongitude" : longitude, "tnameuser" : nameuser, "tcasetype" : desc_type, "tdesc" : desc_data})
	db.commit()

	return jsonify(status = "success")

@app.route("/police/getcase") # java local server route : "getcase"
def pgetcasefunc():
	# start get image from output

	# end
	policeid = "sample"
	casedetail = db.execute('select * from casedetail where pid = :tpid',
		{"tpid" : policeid})

	caseid = casedetail[0]
	latitude = casedetail[2]
	longitude = casedetail[3]
	victimname = casedetail[4]
	casetype = casedetail[5]
	description = casedetail[6]

	return "none"


@app.route("/user/acknowledge") # java local server route : "acktosev"
def uackfunc():
	getlink = "sample"
	caseid = "sample"
	db.execute('insert into getlink values(:tcaseid, :tlink)',
		{"tcaseid": caseid, "tlink" : getlink})

	
	return "none"
