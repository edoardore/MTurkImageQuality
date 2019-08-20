from flask import *
import os
import random
import pickle
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


@app.route('/', methods=['GET', 'POST'])
def login():
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
    pickle.dump(render_data, open("amazondata.p", "wb"))
    resp = make_response(render_template('start.html', name=render_data))
    # This is particularly nasty gotcha.
    # Without this header, your iFrame will not render in Amazon
    resp.headers['x-frame-options'] = 'this_can_be_anything'
    return resp


@app.route('/login', methods=['POST'])
def getValue():
    sex = request.form['sex']
    age = request.form['age']
    display = request.form['display']
    distance = request.form['distance']
    render_data = pickle.load(open("amazondata.p", "rb"))
    while (sex == '' or age == '' or display == '' or distance == ''):
        return render_template('start.html', error='Missing value(s)', name=render_data)
    if (sex != '' or age != '' or display != '' or distance != ''):
        client = Client(sex, age, display, distance)
        addClient(client)
        client.getUserID()
        pickle.dump(client, open("client.p", "wb"))
        return redirect(url_for('index'))


@app.route('/index')
def index():
    client = pickle.load(open("client.p", "rb"))
    image = client.getImg()
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], image)
    pickle.dump(client, open("client.p", "wb"))
    return render_template('index.html', imm=full_filename)


@app.route('/indexnext', methods=['POST'])
def get():
    client = pickle.load(open("client.p", "rb"))
    quality = request.form['quality']
    while (quality == '0'):
        image = client.image
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], image)
        return render_template('index.html', imm=full_filename, error='Please move the slider')
    client.increaseHit()
    addVote(client, quality)
    if client.numHIT < 10:
        image = client.getImg()
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], image)
        pickle.dump(client, open("client.p", "wb"))
        return render_template('index.html', imm=full_filename)
    else:
        render_data = pickle.load(open("amazondata.p", "rb"))
        return render_template('end.html', name=render_data)


class Client:
    def __init__(self, sex, age, display, distance):
        self.sex = sex
        self.age = age
        self.display = display
        self.distance = distance
        self.numHIT = 0
        self.image = None
        self.files = os.listdir("static/images")
        self.userID = 0
        self.imageID = 0

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
