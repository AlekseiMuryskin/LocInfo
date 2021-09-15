from flask import Flask, render_template, request, url_for, flash, redirect
from waitress import serve
from wtforms import SelectField
from flask_wtf import FlaskForm
import pyodbc

app=Flask(__name__)
if __name__ == '__main__':
    app.run()


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
    status = cursor.execute("SELECT * FROM status").fetchall()
    stat={}
    for i in status:
        stat[str(i[0])]=i[1]
    source = cursor.execute("SELECT * FROM source_type").fetchall()
    stype={}
    for i in source:
        stype[str(i[0])]=i[1]
    for i in obj:
        i[6]=stat[str(i[6])]
        i[4]=stype[str(i[4])]
    cursor.close()
    return render_template('table_evt.html', posts=obj)

@app.route('/station')
def station():
    cursor = get_db_connect()
    obj = cursor.execute("SELECT DISTINCT sta_code,X,Y,Z FROM channel").fetchall()
    cursor.close()
    for i in obj:
        i[1]=f'{i[1]:.2f}'
        i[2] = f'{i[2]:.2f}'
        i[3] = f'{i[3]:.2f}'
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
    return render_template('create_obj.html', code=code)


@app.route('/edit_obj_all/<code>',methods=('GET','POST'))
def edit_obj_all(code):
    cursor = get_db_connect()
    obj = cursor.execute(f"SELECT * FROM object WHERE code = '{code}'").fetchall()
    cursor.close()
    if request.method == 'POST':
        data = request.form.to_dict()
        desc=data['description']
        corn=data['corners']
        xc=data['Xc']
        yc=data['Yc']
        coo=data['Coord system']
        cursor = get_db_connect()
        cursor.execute(f"UPDATE object SET description = '{desc}',corners = '{corn}',xc = {float(xc)}, yc = {float(yc)}, coord_system = '{coo}' WHERE code = '{code}'")
        cursor.commit()
        cursor.close()
        return redirect(url_for('index'))
    return render_template('edit_obj_all.html',posts=obj[0])

@app.route('/edit_obj',methods=('GET','POST'))
def editObj():
    cursor = get_db_connect()
    obj = cursor.execute("SELECT code FROM object").fetchall()
    cursor.close()
    if request.method == 'POST':
        code = request.form['code']
        cursor = get_db_connect()
        obj_info = cursor.execute(f"SELECT * FROM object WHERE code = '{code}'").fetchall()
        cursor.close()
        redirect(url_for('index'))
        return redirect(url_for('edit_obj_all',code=code))
    return render_template('edit_obj.html',posts=obj)

@app.route('/delete_obj',methods=('GET','POST'))
def deleteObj():
    cursor = get_db_connect()
    obj = cursor.execute("SELECT code FROM object").fetchall()
    cursor.close()
    names=",".join([i[0] for i in obj])
    if request.method == 'POST':
        code = request.form['code']
        if not code:
            flash('Code is requiered')
        else:
            conn=get_db_connect()
            conn.execute(f"DELETE FROM object WHERE code='{code}'")
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('delete_obj.html',names=names)


@app.route('/edit_sta',methods=('GET','POST'))
def editSta():
    cursor = get_db_connect()
    obj = cursor.execute("SELECT code FROM station").fetchall()
    cursor.close()
    if request.method == 'POST':
        code = request.form['code']
        cursor = get_db_connect()
        obj_info = cursor.execute(f"SELECT * FROM station WHERE code = '{code}'").fetchall()
        cursor.close()
        redirect(url_for('index'))
        return redirect(url_for('edit_sta_all',code=code))
    return render_template('edit_sta.html',posts=obj)

@app.route('/edit_sta_all/<code>',methods=('GET','POST'))
def edit_sta_all(code):
    cursor = get_db_connect()
    obj = cursor.execute(f"SELECT * FROM station WHERE code = '{code}'").fetchall()
    cursor.close()
    if request.method == 'POST':
        data = request.form.to_dict()
        desc=data['description']
        net=data['Net']
        coo=data['Coord system']
        start=data['start']
        end=data['end']
        cursor = get_db_connect()
        cursor.execute("UPDATE station SET description = '%s', net = '%s', coord_system = '%s' WHERE code = '%s'" % (desc,net,coo,code))
        cursor.commit()
        cursor.close()
        return redirect(url_for('index'))
    return render_template('edit_sta_all.html',posts=obj[0])

@app.route('/edit_chan',methods=('GET','POST'))
def channel_edit():
    cursor = get_db_connect()
    obj = cursor.execute("SELECT code FROM station").fetchall()
    cursor.close()
    lc=[]
    ch=[]
    if request.method == 'POST':
        code = request.form['code']
        try:
            locid=request.form['loc']
            channel = request.form['chan']
            redirect(url_for('index'))
            return redirect(url_for('edit_chan_all', code=code, locid=locid, channel=channel))
        except:
            cursor = get_db_connect()
            obj_info = cursor.execute(f"SELECT code,lc FROM channel WHERE sta_code = '{code}'").fetchall()
            cursor.close()
            for i in obj_info:
                ch.append(i[0])
                lc.append(i[1])
            lc=list(set(lc))
            return render_template('edit_chan.html', posts=obj, lc=lc, ch=ch)

        #locid=request.form['loc']
        #channel=request.form['chan']
        #redirect(url_for('index'))
        #return redirect(url_for('edit_chan_all', code=code,locid=locid,channel=channel))
    return render_template('edit_chan.html',posts=obj,lc=lc,ch=ch)

@app.route('/edit_chan_all/<code>/<locid>/<channel>',methods=('GET','POST'))
def edit_chan_all(code,locid,channel):
    cursor = get_db_connect()
    obj = cursor.execute(f"SELECT * FROM channel WHERE (sta_code = '{code}') AND (lc = '{locid}') AND  (code = '{channel}')").fetchall()
    cursor.close()
    if request.method == 'POST':
        data = request.form.to_dict()
        sta=data['sta']
        new_code=data['code']
        dip=data['dip']
        freq=data['freq']
        loc=data['loc']
        norm=data['norm']
        sens=data['sens']
        x=data['x']
        y=data['y']
        z=data['z']
        poles=data['poles']
        zeros=data['zeros']
        az=data['az']
        cursor = get_db_connect()
        cursor.execute("UPDATE channel SET sta_code='%s',code='%s',lc='%s',X='%s',Y='%s',Z='%s',azimuth='%s',dip='%s',sensitivity='%s',sensitivity_freq='%s',poles='%s',zeros='%s',norm_coefficient='%s'  WHERE sta_code = '%s' AND lc = '%s' AND code = '%s'" % (sta,new_code,loc,x,y,z,az,dip,sens,freq,poles,zeros,norm,code,locid,channel))
        #cursor.execute(
        #    "UPDATE channel SET sta_code='%s',code='%s',lc='%s',X='%s',Y='%s',Z='%s',azimuth='%s',dip='%s',sensitivity='%s',sensitivity_freq='%s'  WHERE sta_code = '%s' AND lc = '%s' AND code = '%s'" % (
        #    sta, new_code, loc, x, y, z, az, dip, sens, freq, code, locid, channel))
        cursor.commit()
        cursor.close()
        return redirect(url_for('index'))
    return render_template('edit_chan_all.html',posts=obj[0])


def get_db_connect():
    #db = 'D:\git\FlaskStep\loc_db_v3.accdb'
    db = 'E:\git\LocInfo\loc_db_v3.accdb'
    try:
        con_str = f'DBQ={db};'
        con_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};' + con_str
        conn = pyodbc.connect(con_string)
        print("Connected To Database")
    except pyodbc.Error as e:
        print("Error in Connection", e)
    cursor = conn.cursor()
    return cursor





