import pymysql
import os

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


initalization()  # run this module the first time ever, you need to set up MYSQL dbms earlier (e.g. PhpMyAdmin in XAMPP).
# after the execution, recomment this line with
