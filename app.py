from flask import *
import os
import random
import pymysql
import ssl

# Start Configuration Variables
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
DEV_ENVIROMENT_BOOLEAN = True
DEBUG = True
# End Configuration Variables

# This allows us to specify whether we are pushing to the sandbox or live site.
if DEV_ENVIROMENT_BOOLEAN:
    AMAZON_HOST = "https://workersandbox.mturk.com/mturk/externalSubmit"
else:
    AMAZON_HOST = "https://www.mturk.com/mturk/externalSubmit"

app = Flask(__name__)

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain("miocert.crt", "miocert.key")

IMAGE_FOLDER = os.path.join('static', 'images')
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER


def getUserID():
    db = pymysql.connect("localhost", "testuser", "test123", "mysqldb")
    cursor = db.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT MAX(USER_ID) FROM client"
    cursor.execute(sql)
    uid = cursor.fetchone()
    return uid


def getImageID(Client):
    db = pymysql.connect("localhost", "testuser", "test123", "mysqldb")
    cursor = db.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT Image_ID FROM images WHERE IMAGE_FILE=('%s')" % (Client.image)
    cursor.execute(sql)
    uid = cursor.fetchone()
    return uid


def addClient(Client):
    db = pymysql.connect("localhost", "testuser", "test123", "mysqldb")
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # Prepare SQL query to INSERT a record into the database.
    sql = "INSERT INTO client(USER_AGE, USER_SEX,USER_MONITOR, USER_DISTANCE)VALUES " \
          "('%s', '%s', '%s', '%s')" % (
              Client.age, Client.sex, Client.display, Client.distance)
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()
    # disconnect from server
    db.close()


def addVote(Client, vote):
    db = pymysql.connect("localhost", "testuser", "test123", "mysqldb")
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    imageID = int(Client.imageID.get("Image_ID"))
    userID = int(Client.userID.get("MAX(USER_ID)"))
    vote = int(vote)
    # Prepare SQL query to INSERT a record into the database.
    sql = "INSERT INTO valutation(IMAGE_ID, USER_ID, USER_VOTE)VALUES " \
          "('%s', '%s', '%s')" % (imageID, userID, vote)
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()
    # disconnect from server
    db.close()


clientsConnected = []


@app.route('/', methods=['GET', 'POST'])
def login():
    client = Client()
    clientsConnected.append(client)
    # The following code segment can be used to check if the turker has accepted the task yet
    if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
        # Our worker hasn't accepted the HIT (task) yet
        pass
    else:
        # Our worker accepted the task
        pass
    render_data = {
        "worker_id": request.args.get("workerId"),
        "assignment_id": request.args.get("assignmentId"),
        "amazon_host": AMAZON_HOST,
        "hit_id": request.args.get("hitId"),
        "turk_submit_to": request.args.get("turkSubmitTo")
    }
    resp = make_response(render_template('start.html', name=render_data))
    # Without this header, your iFrame will not render in Amazon
    resp.headers['x-frame-options'] = 'this_can_be_anything'
    client.ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    client.workerID = render_data['worker_id']
    client.assignmentID = render_data['assignment_id']
    client.hitID = render_data['hit_id']
    client.turkSubmitTo = render_data['turk_submit_to']
    return resp


@app.route('/login', methods=['POST'])
def getValue():
    sex = request.form['sex']
    age = request.form['age']
    display = request.form['display']
    distance = request.form['distance']
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    for c in clientsConnected:
        if c.ip == ip:
            render_data = {
                "worker_id": c.workerID,
                "assignment_id": c.assignmentID,
                "amazon_host": AMAZON_HOST,
                "hit_id": c.hitID,
                "turk_submit_to": c.turkSubmitTo
            }
    while (sex == '' or age == '' or display == '' or distance == ''):
        return render_template('start.html', error='Missing value(s)', name=render_data)
    if (sex != '' or age != '' or display != '' or distance != ''):
        for c in clientsConnected:
            if c.ip == ip:
                c.sex = sex
                c.age = age
                c.display = display
                c.distance = distance
                addClient(c)
                c.getUserID()
                break
        return redirect(url_for('index'))


@app.route('/index')
def index():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    for c in clientsConnected:
        if c.ip == ip:
            image = c.getImg()
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], image)
    return render_template('index.html', imm=full_filename)


@app.route('/indexnext', methods=['POST'])
def get():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    quality = request.form['quality']
    while (quality == '0'):
        for c in clientsConnected:
            if c.ip == ip:
                image = c.image
                break
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], image)
        return render_template('index.html', imm=full_filename, error='Please move the slider')
    for c in clientsConnected:
        if c.ip == ip:
            c.increaseHit()
            addVote(c, quality)
            if c.numHIT < 10:
                image = c.getImg()
                full_filename = os.path.join(app.config['UPLOAD_FOLDER'], image)
                return render_template('index.html', imm=full_filename)
            else:
                render_data = {
                    "worker_id": c.workerID,
                    "assignment_id": c.assignmentID,
                    "amazon_host": AMAZON_HOST,
                    "hit_id": c.hitID,
                    "turk_submit_to": c.turkSubmitTo
                }
                clientsConnected.remove(c)
                return render_template('end.html', name=render_data)


class Client:
    def __init__(self):
        self.sex = None
        self.age = None
        self.display = None
        self.distance = None
        self.numHIT = 0
        self.image = None
        self.files = os.listdir("static/images")
        self.userID = None
        self.imageID = None
        self.ip = None
        self.workerID = None
        self.assignmentID = None
        self.hitID = None
        self.turkSubmitTo = None

    def increaseHit(self):
        self.numHIT += 1

    def getUserID(self):
        self.userID = getUserID()

    def getImgID(self):
        self.imageID = getImageID(self)

    def getImg(self):
        file = self.files.pop(random.randrange(len(self.files)))
        self.image = file
        self.imageID = getImageID(self)
        return file


if __name__ == '__main__':
    app.run(debug=True, ssl_context=context, host='192.168.1.79')
