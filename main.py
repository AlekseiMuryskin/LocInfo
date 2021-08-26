from flask import Flask, render_template, request, url_for, flash, redirect
import pyodbc

app=Flask(__name__)
app.config['SECRET_KEY']='pts'

@app.route('/')
def index():
    cursor=get_db_connect()
    obj=cursor.execute("SELECT code,description FROM object").fetchall()
    cursor.close()
    return render_template('index.html', posts=obj)

@app.route('/object')
def object():
    cursor = get_db_connect()
    obj = cursor.execute("SELECT * FROM object").fetchall()
    cursor.close()
    for i in obj:
        i[3]=f'{i[3]:.2f}'
        i[4]=f'{i[4]:.2f}'
    return render_template('table_obj.html', posts=obj)

@app.route('/evt')
def event():
    cursor = get_db_connect()
    obj = cursor.execute("SELECT * FROM event").fetchall()
    cursor.close()
    return render_template('table_evt.html', posts=obj)

@app.route('/station')
def station():
    cursor = get_db_connect()
    obj = cursor.execute("SELECT * FROM channel").fetchall()
    cursor.close()
    for i in obj:
        i[4]=f'{i[4]:.2f}'
        i[5] = f'{i[5]:.2f}'
        i[6] = f'{i[6]:.2f}'
        i[11] = f'{i[11]:.2e}'
        i[15] = f'{i[15]:.2e}'
    return render_template('table_sta.html', posts=obj)

@app.route('/create_obj',methods=('GET','POST'))
def createObj():
    if request.method == 'POST':
        code = request.form['code']
        desc = request.form['desc']
        corn = request.form['corn']
        xc = request.form['xc']
        yc = request.form['yc']
        coord = request.form['coord']

        if not code:
            flash('Code is required!')
        else:
            conn = get_db_connect()
            conn.execute('INSERT INTO object (code, description, corners,xc,yc,coord_system) VALUES (?, ?, ?, ?, ?, ?)',
                         (code, desc,corn,float(xc),float(yc),coord))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('create_obj.html')

@app.route('/edit_obj',methods=('GET','POST'))
def editObj():
    cursor = get_db_connect()
    obj = cursor.execute("SELECT code FROM object").fetchall()
    cursor.close()
    if request.method == 'POST':
        code = request.form['code']
        cursor = get_db_connect()
        obj_info = cursor.execute("SELECT description,corners,xc,yc,coord_system FROM object WHERE code=VALUES(?)",
                                  (code)).fetchall()
        cursor.close()
        return redirect('edit_obj_all')
    return render_template('edit_obj.html',posts=obj)

@app.route('/edit_obj_all',methods=('GET','POST'))
def editObjAll():
    if request.method == 'POST':
        code = request.form['code']
        cursor = get_db_connect()
        obj_info = cursor.execute("SELECT description,corners,xc,yc,coord_system FROM object WHERE code=VALUES(?)",(code)).fetchall()
        cursor.close()
        return obj_info
    return render_template('edit_obj_all.html')

@app.route('/delete_obj',methods=('GET','POST'))
def deleteObj():
    if request.method == 'POST':
        code = request.form['code']
        if not code:
            flash('Code is requiered')
        else:
            conn=get_db_connect()
            conn.execute('DELETE FROM object WHERE code=VALUES(?)',(code))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('delete_obj.html')

def get_db_connect():
    db = 'D:\git\FlaskStep\loc_db_v3.accdb'
    try:
        con_str = f'DBQ={db};'
        con_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};' + con_str
        conn = pyodbc.connect(con_string)
        print("Connected To Database")
    except pyodbc.Error as e:
        print("Error in Connection", e)
    cursor = conn.cursor()
    return cursor
