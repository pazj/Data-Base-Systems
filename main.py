from flask import Flask, render_template, redirect, request, url_for, jsonify, session
import psycopg2 as pg 
import psycopg2.extras
import csv

app = Flask(__name__)

#connecting to psql database
db_connect = {
        'host': 'localhost',
        'port': '5432',
        'user': 'postgres',
        'dbname': 'deliveryhanyang',
        'password':'paraguay21'
    }
    
conn_str = connect_string = "host={host} port={port} user={user} dbname={dbname} password={password}".format(**db_connect)


def create_tables():
    
    #open cursor to perform database operations
    conn = pg.connect(connect_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    #create tables in the psql database  
    sql = (
        """
        CREATE TABLE customer(
            name VARCHAR(500),
            phone INTEGER,
            local VARCHAR(255),
            domain VARCHAR(255),
            password VARCHAR(255),
            payments VARCHAR(500),
            lat numeric(6,4),
            long numeric(8,5),
            PRIMARY KEY(name)
        
        )
        """,
        """CREATE TABLE bank(
            bid integer NOT NULL,
            Code INTEGER,
            bname VARCHAR(255),
            PRIMARY KEY(bid)

        )
        """,
        """CREATE TABLE delivery(
            did INTEGER NOT NULL,
            d_name VARCHAR(255),
            d_phone INTEGER,
            d_local VARCHAR(255),
            d_domain VARCHAR(255),
            d_password VARCHAR(255),
            d_lat numeric(6,4),
            d_lng numeric(8,5),
            stock INTEGER,
            PRIMARY KEY (did)
        )
        """,
        """CREATE TABLE menu(
            menu VARCHAR(100),
            m_sid INTEGER,
            PRIMARY KEY(m_sid)
        )
        """,
        """CREATE TABLE seller(
            s_sid integer NOT NULL,
            s_name CHAR(20),
            s_phone INTEGER,
            s_local VARCHAR(255),
            s_domain VARCHAR(255),
            s_password VARCHAR(255)
            PRIMARY KEY(s_sid)
        )
        """,
        """ CREATE TABLE store(
            store_sid integer NOT NULL,
            store_address VARCHAR(255),
            sname VARCHAR(255),
            lat_s numeric(6,4),
            lng_s numeric(6,3),
            phone_nums VARCHAR(255),
            schedules VARCHAR(500),
            PRIMARY KEY (store_sid)
        )
        """)
    
    try:
        for db_connect in sql :
            cur.execute(db_connect)
        #commit the changes
        conn.commit()
        cur.close()
       
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
def insert_files():
    
    conn = pg.connect(connect_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    with open('customer.csv', 'r') as f:
        next(f)
        cur.copy_from(f,'customer', sep=';')
    conn.commit()

    with open('seller.csv', 'r') as f:
        next(f)
        cur.copy_from(f,'seller', sep=';')
    conn.commit()

    with open('delivery.csv', 'r') as f:
        next(f)
        cur.copy_from(f,'delivery', sep=';')
    conn.commit()

    with open('bank.csv', 'r') as f:
        next(f)
        cur.copy_from(f,'bank', sep=';')
    conn.commit()

    with open('menu.csv', 'r') as f:
        next(f)
        cur.copy_from(f,'menu', sep=';')
    conn.commit()

    with open('store.csv', 'r') as f:
        next(f)
        cur.copy_from(f,'store', sep=';')
    conn.commit()

   
@app.route("/")
def index():
    conn = pg.connect(conn_str)
    cur = conn.cursor()
    sid = '10'
    sql = f"SELECT s_sid, s_name, s_phone, s_local,s_domain, s_password FROM seller WHERE s_sid ={sid}"
    print(sql)
    
    cur.execute(sql)
    rows = cur.fetchall()
    
    return render_template("index.html", msg=rows)


@app.route('/login', methods=['POST'])
def login():
    local = request.form.get('sid')
    passwd = request.form.get('passwd')
    _id = local.split('@')
    conn = pg.connect(conn_str)
    cur = conn.cursor()
    sql = f"SELECT * FROM customer WHERE local ='{_id[0]}'AND domain = '{_id[1]}'  AND password = '{passwd}'"
    _type = 'customer'
    cur.execute(sql)
    rows = cur.fetchal

    if len(rows) == 0:
        sql = f"SELECT * FROM seller WHERE s_local ='{_id[0]}'AND s_domain = '{_id[1]}'  AND s_password = '{passwd}'"
        _type = 'seller'
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) == 0:
            sql = f"SELECT * FROM delivery WHERE d_local ='{_id[0]}'AND d_domain = '{_id[1]}'  AND d_password = '{passwd}'"
            _type = 'delivery'
            cur.execute(sql)
            rows = cur.fetchall()
            print(sql)
            print(len(rows))
            if len(rows) == 0:
                _type = 'wrong'
    '''if(len(rows) !=1):
        return render_template('error.html', msg="Wrong ID")
    print((rows[0]))'''


    conn.close()

    if (_type == 'seller') : 
        return redirect("/seller")
    elif (_type == 'customer'):
        return redirect("/customer")
    elif (_type == 'delivery'):
        return redirect("/delivery")
    else :
        return redirect("/delivery")

@app.route('/seller', methods=['GET', 'POST'])
def seller():
    conn = pg.connect(conn_str)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sid = '12'
    sql = f"SELECT sid, name, phone, local,domain, passwd FROM seller WHERE sid ={sid}"
    print(sql)

    cur.execute(sql)
    rows = cur.fetchall()
    print(rows)
    if request.method == 'POST':
        return redirect(url_for('index.html'))

    else:
        #show the form, it wasn't submitted
        return render_template('seller.html',seller_data=rows)

@app.route('/customer', methods= ['GET', 'POST'])
def customer():
    conn = pg.connect(conn_str)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    local = request.form.get('name')
    _id = local.split('@')
    name = '박희진'
    sql = f"SELECT name, phone, local, domain, passwd, payments, lat, lng FROM customer WHERE name ={name}"
    print(sql)
    cur.execute(sql)
    rows = cur.fetchall()
    print(rows)
    if request.method == "POST":
        return redirect(url_for('index'))
    else:
       return render_template('customer.html', customer_data=rows)


@app.route('/delivery', methods=['GET', 'POST'])
def delivery():
    conn = pg.connect(conn_str)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    did = '5'
    sql = f"SELECT did, name, phone, local, domain, passwd, lat, lng, stock FROM delivery WHERE did={did}"
    print(sql)
    cur.execute(sql)
    rows = cur.fetchall()
    print(rows)
    if request.method == 'POST':
        return redirect(url_for('index'))

    else:
        # show the form, it wasn't submitted
        return render_template('delivery.html', delivery_data=rows)



if __name__ == "__main__":
    #create_tables()
    app.run(debug=True)
