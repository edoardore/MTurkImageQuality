from flask import *
import os
import random
import pickle
import pymysql

app = Flask(__name__)

IMAGE_FOLDER = os.path.join('static', 'images')
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER


def initalization():
    # Open database connection
    db = pymysql.connect("localhost", "testuser", "test123", "mysqldb")
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS images")
    # Create table as per requirement
    sql = """CREATE TABLE `mysqldb`.`images`(`IMAGE_ID` INT NOT NULL AUTO_INCREMENT, `IMAGE_FILE` VARCHAR(100) 
    NOT NULL, PRIMARY KEY (IMAGE_ID))ENGINE = InnoDB;"""
    # Execute the SQL command
    cursor.execute(sql)
    # disconnect from server
    db.close()
    # Open database connection
    db = pymysql.connect("localhost", "testuser", "test123", "mysqldb")
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    files = os.listdir("static/images")
    for i in range(0, len(files)):
        # Prepare SQL query to INSERT a record into the database.
        sql = "INSERT INTO images(IMAGE_ID, IMAGE_FILE)VALUES ('%s', '%s')" % (i, files[i])
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
    # Open database connection
    db = pymysql.connect("localhost", "testuser", "test123", "mysqldb")
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS valutation")
    # Create table as per requirement
    sql = """CREATE TABLE `mysqldb`.`valutation`(`IMAGE_ID` INT NOT NULL, USER_ID INT NOT NULL, 
        USER_VOTE INT NOT NULL)ENGINE = InnoDB;"""
    # Execute the SQL command
    cursor.execute(sql)
    # disconnect from server
    db.close()
    # Open database connection
    db = pymysql.connect("localhost", "testuser", "test123", "mysqldb")
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS client")
    # Create table as per requirement
    sql = """CREATE TABLE `mysqldb`.`client`(USER_ID INT NOT NULL AUTO_INCREMENT, USER_AGE INT NOT NULL,
                USER_SEX VARCHAR(1), USER_MONITOR VARCHAR(10), USER_DISTANCE VARCHAR(3), PRIMARY KEY (USER_ID))ENGINE = InnoDB;"""
    # Execute the SQL command
    cursor.execute(sql)
    # disconnect from server
    db.close()


#initalization()  # run this line the first time ever, you need to set up MYSQL dbms earlier (e.g. PhpMyAdmin in XAMPP).
# after the execution, recomment this line with #


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


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def getValue():
    sex = request.form['sex']
    age = request.form['age']
    display = request.form['display']
    distance = request.form['distance']
    while (sex == '' or age == '' or display == '' or distance == 0):
        return render_template('login.html', error='Missing value(s)')
    if (sex != '' or age != '' or display != '' or distance != 0):
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
    client.increaseHit()
    addVote(client, quality)
    if client.numHIT < 10:
        image = client.getImg()
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], image)
        pickle.dump(client, open("client.p", "wb"))
        return render_template('index.html', imm=full_filename)
    else:
        return 'Finish!'


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
    app.run(debug=True)
