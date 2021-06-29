from flask import Flask, jsonify, make_response, request, render_template
from redis import Redis, RedisError
from flask_sqlalchemy import SQLAlchemy
#from flask_script import Manager
#from flask_migrate import Migrate, MigrateCommand
from sqlalchemy.exc import OperationalError
import psycopg2

import os
import socket
import time
import json
import sys

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)


app = Flask(__name__)
#https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/#flask_sqlalchemy.SQLAlchemy.engine
#postgresql:/URI format
#postgresql://scott:tiger@localhost/mydatabase

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://objectrocket:orkb123@10.144.180.121:5432/ordb'
app.config.from_pyfile('config.cfg')
db = SQLAlchemy()
db.init_app(app)

timeout = time.time() + 100 * 5

@app.route("/getEnv")
def getEnv():
    db_name = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    pwd = os.environ['POSTGRES_PASSWORD']
    return db_name

#The baseclass for all your models is called db.Model
#https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
#To override the table name, set the __tablename__ class attribute

class User(db.Model):
    __tablename__ = 'info_table'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String())
    age = db.Column(db.Integer())

    def __init__(self, name,age):
        self.name = name
        self.age = age

    def __repr__(self):
        return '<User %r>' % self.username


def fecth_db(cursor, table_name):
    page = "fecth_db"
    # Fetch result
    cursor.execute("SELECT * from {} ;".format(table_name))
    page += "Fetch result"
    records = cursor.fetchall()
    for row in records:
        page += "surname = " + row[0]
        page += "givename = " + row[1]
    return page

def table_exists(con, table_name):
    page = "table "
    exists = False
    try:
        cur = con.cursor()
        cur.execute("select exists(select relname from pg_class where relname='" + table_name + "')")
        exists = cur.fetchone()[0]
        page +=  table_name + " exists"
        cur.close()
    except psycopg2.Error as e:
        page += e
    return page, exists

def get_table_col_names(con, table_str):
    page = "get column name: "
    col_names = []
    try:
        cur = con.cursor()
        cur.execute("select * from " + table_str + " LIMIT 0")
        for desc in cur.description:
            page += desc[0]
            col_names.append(desc[0])
        cur.close()
    except psycopg2.Error as e:
        page += e

    return page, col_names

#https://www.psycopg.org/docs/usage.html
#https://pynative.com/python-postgresql-select-data-from-table/

def add_User(conn, table_name, surname, givename):
    page = "insert "
    error = 0
    try:
        cur = conn.cursor()
        insert_query = "INSERT INTO %s (NOM, PRENOM) VALUES ('%s', '%s');"%(table_name, surname, givename)
        #insert_query = "INSERT INTO %s (NOM, PRENOM) VALUES ('leo','rania');"%(table_name)
        page += "insert query " + insert_query
        cur.execute(insert_query)
        page += " cur.execute " + insert_query + " OK"
        conn.commit()
    except Exception as ex:
        page += repr(ex)
        error = 2
    return page, error


@app.route('/getConnect', methods=['GET', 'POST'])
def getConnect():
    page ="Param: "
    server = "127.0.0.0"
    port= "5432"
    db_name = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    pwd = os.environ['POSTGRES_PASSWORD']
    #server = os.environ['POSTGRES_HOST']
    #port = os.environ['POSTGRES_PORT']
    nom = "NONE"
    prenom = "NONE"

    conn = None
    table_name = "customer_table"

    for text in request.form:
        if (text == 'HOST'):
            server = request.form['HOST']
            page += server
        if (text == "Port"):
            port = request.form['Port']
            page += port
        if (text == "Table"):
            table_name = request.form['Table']
            page += table_name
        if (text == "Nom"):
            nom = request.form['Nom']
            page += nom
        if (text == "Prenom"):
            prenom = request.form['Prenom']
            page += prenom
            
    config = "postgresql://" +user+ ":" +pwd + "@" + server + ":" + port + "/" + db_name
    page = config
    cnx = "host={} dbname= {} user={} password={}".format(server, db_name, user, pwd)
    #connection = "host=%s dbname=%s user=%s password=%s"% (HOST, DATABASE,USER, PASSWORD))
    return cnx

@app.route('/create_db', methods=['GET', 'POST'])
def create_db():
    page ="Param: "
    server = "127.0.0.0"
    port= "5432"
    db_name = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    pwd = os.environ['POSTGRES_PASSWORD']
    #server = os.environ['POSTGRES_HOST']
    #port = os.environ['POSTGRES_PORT']
    nom = "NONE"
    prenom = "NONE"

    conn = None
    table_name = "customer_table"

    for text in request.form:
        if (text == 'HOST'):
            server = request.form['HOST']
            page += server
        if (text == "Port"):
            port = request.form['Port']
            page += port
        if (text == "Table"):
            table_name = request.form['Table']
            page += table_name
        if (text == "Nom"):
            nom = request.form['Nom']
            page += nom
        if (text == "Prenom"):
            prenom = request.form['Prenom']
            page += prenom

    config = "postgresql://" +user+ ":" +pwd + "@" + server + ":" + port + "/" + db_name
    page = config
    cnx = "host={} dbname= {} user={} password={}".format(server, db_name, user, pwd)
    #connection = "host=%s dbname=%s user=%s password=%s"% (HOST, DATABASE,USER, PASSWORD))

    try:
        #conn = psycopg2.connect(server, user, pwd, port, db_name)
        conn = psycopg2.connect(cnx)

        page += "--- connect OK "
        cur = conn.cursor()

        sql = "CREATE TABLE IF NOT EXISTS {} (NOM TEXT, PRENOM TEXT);".format(table_name)
        page += sql
        cur.execute(sql)
        conn.commit()
        page += "--- Table {}created successfully in PostgreSQL".format(table_name)

        txt, exists = table_exists(conn, table_name)
        page += txt

        if (exists == True):
            txt,col_names = get_table_col_names(conn, table_name)
            page += txt
            txt = fecth_db(cur, table_name)
            page += txt


        txt, rcode  = add_User(conn, table_name, nom, prenom)
        if (rcode == 0):
            page += "--- add_user OK " + txt
        else:
            page += "--- add_user ERROR " + txt

        # Fetch result
        cur.execute("SELECT * from {} ;".format(table_name))
        page += "Fetch result"
        records = cur.fetchall()
        for row in records:
            page += "surname = " + row[0]
            page += "givename = " + row[1]

        cur.execute("DROP TABLE IF EXISTS {};".format(table_name))
        conn.commit()
        page += "--- drop table OK "
        conn.close()
        page += "--- close OK "
    except psycopg2.Error as error:
        page += 'Unable to connect!\n{0}'.format(error)
        page += repr(error)
        return page
    except Exception as ex:
        message = ex.__class__.__name__
        exc_type, value, traceback = sys.exc_info()
        page += exc_type.__name__
        page += repr(ex)
        return page

    return page

#http://10.1.1.1:5000/login?username=alex&password=pw1
@app.route('/login', methods=['POST'])
def login():
    page = "Login"
    username = request.args.get('username')
    page += username
    password= request.args.get('password')
    page += password
    return page


#https://pythonbasics.org/flask-sqlalchemy/
@app.route('/show_all')
def show_all():
    page = "show_all"
    template = "./show_users.html"
    page = render_template(template, users = User.query.all())
    return page

@app.route('/add/<name>')
def add(name):
    db_name = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    pwd = os.environ['POSTGRES_PASSWORD']
    page = "test_db - "

    try:
        app.config.from_pyfile('config.cfg')
        config = app.config['SQLALCHEMY_DATABASE_URI']
        page += config

        me = User(name, 58)
        db.session.add(me)
        db.session.commit()

        user = User.query.first()
        page += "First User '{} {}' is from database".format(user.name, user.age)

        current = User.query.filter_by(name=name).first()
        page += "Addess User '{} {}' is from database".format(current.name, current.age)


    except Exception as ex:
        message = ex.__class__.__name__
        exc_type, value, traceback = sys.exc_info()
        page += exc_type.__name__
        page += repr(ex)

    return page


@app.route('/test_db')
def test_db():
    db_name = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    pwd = os.environ['POSTGRES_PASSWORD']
    page = "test_db - "
    config = app.config['SQLALCHEMY_DATABASE_URI']
    page += "Connection URI Format:" + config

    try:
        db.create_all()
        page += "create - "
        db.session.commit()
        page += "commit - "
        user = User.query.first()
        if not user:
            u = User(name='Leonard', age=58)
            db.session.add(u)
            db.session.commit()
        user = User.query.first()
        return "User '{} {}' is from database".format(user.name, user.age)
    except:
        return page



@app.route("/contact")
def contact():
    mail = "leonard.rania@fr.ibm.com"
    tel = "01 23 45 67 89"
    return "Mail: {} --- Tel: {}".format(mail, tel)

@app.route("/healthz/ready")
def readiness():
    time.sleep(1)
    return "OK"

@app.route("/healthz/live", methods=['GET'])
def liveness():
    headers = {'Content-Type': 'text/plain'}
    delay = time.time()
    if (delay < timeout):
        return "OK", 200, {'Content-Type': 'text/plain'}
    else:
        return "timeout", 408, {'Content-Type': 'text/plain'}

@app.route("/")
def hello():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>" \
           "<b>Visits:</b> {visits}"
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), visits=visits)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
