from flask import Flask, render_template, request, url_for, flash, redirect
import pyodbc
from obspy import UTCDateTime

app=Flask(__name__)
if __name__ == '__main__':
    app.run(debug=True)

"""
Веб-сервер для работы с БД Location3
"""

#рендер главной страницы
@app.route('/')
def index():
    cursor=get_db_connect()
    obj=cursor.execute("SELECT code,description FROM object").fetchall()
    cursor.close()
    return render_template('index.html', posts=obj)

#рендер страницы Object
@app.route('/object')
def object():
    cursor = get_db_connect()
    obj = cursor.execute("SELECT * FROM object").fetchall()
    cursor.close()
    for i in obj:
        i[3]=f'{i[3]:.2f}'
        i[4]=f'{i[4]:.2f}'
    return render_template('table_obj.html', posts=obj)

#рендер страницы Event. ПОСТ-запрос позволяет проводить фильтрацию табличных данных, которые видит пользователь
@app.route('/evt',methods=('GET','POST'))
def event():
    active_filter=''
    cursor = get_db_connect()
    obj = cursor.execute("SELECT * FROM event").fetchall()
    status = cursor.execute("SELECT * FROM status").fetchall()
    code_obj= cursor.execute("SELECT code FROM object").fetchall()
    stat={}
    for i in status:
        stat[str(i[0])]=i[1]
    source = cursor.execute("SELECT * FROM source_type").fetchall()
    stype={}
    dat=[]
    for i in source:
        stype[str(i[0])]=i[1]
    for i in obj:
        dat.append(decodeID(i[0]))
        i[6]=stat[str(i[6])]
        i[4]=stype[str(i[4])]
    cursor.close()

    if request.method == 'POST':
        code=request.form['code']
        active_filter='Filters: '
        if len(code)>0:
            obj=list(filter(lambda x:code in x,obj))
            active_filter+=code+' '
        filtstat = request.form['status']
        if len(filtstat) > 0:
            obj = list(filter(lambda x: filtstat in x, obj))
            active_filter+= filtstat+' '
        filtsource = request.form['source']
        if len(filtsource) > 0:
            obj = list(filter(lambda x: filtsource in x, obj))
            active_filter += filtsource + ' '
        start=request.form['start']
        end=request.form['end']
        obj2=[]
        if len(start)>0 and len(end)>0:
            t1=UTCDateTime(start+'T00:00')
            t2=UTCDateTime(end+'T00:00')
            for i in range(len(obj)):
                if dat[i]>=t1 and dat[i]<=t2:
                    obj2.append(obj[i])
            obj=obj2
            active_filter+=start+' '+end+' '
        auto=request.form['auto']
        if len(auto)>0:
            if auto=='Auto':
                obj=list(filter(lambda x:True in x,obj))
            else:
                obj=list(filter(lambda x:False in x,obj))
            active_filter+=auto+' '
        limit = request.form['limit']
        if len(limit)>0:
            obj=obj[:int(limit)]
            active_filter+='limit '+limit
        return render_template('table_evt.html', posts=obj, obj=code_obj,status=status,sources=source,filter=active_filter)
    return render_template('table_evt.html', posts=obj,obj=code_obj,status=status,sources=source,filter=active_filter)

#рендер страницы Station
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

#страница создания нового объекта
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

#страница редактирования параметров уже существующего объекта с динамической маршрутизацией
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

#страница выбора объекта для редактирования
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

#страница удаления объекта
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

#страница редактирования станции
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

#редактирование параметров выбранной станции
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

#выбор канала для редактирования
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
    return render_template('edit_chan.html',posts=obj,lc=lc,ch=ch)

#редактирование параметров выбранного канала
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

#подклюбчение к БД
def get_db_connect():
    db = 'D:\git\FlaskStep\loc_db_v3.accdb'
    #db = 'E:\git\LocInfo\loc_db_v3.accdb'
    try:
        con_str = f'DBQ={db};'
        con_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};' + con_str
        conn = pyodbc.connect(con_string)
        print("Connected To Database")
    except pyodbc.Error as e:
        print("Error in Connection", e)
    cursor = conn.cursor()
    return cursor


#создание уникального ID для сейсмических событий
def CreatID(dat,code):
    #новая система счисления
    abc=[0,1,2,3,4,5,6,7,8,9,'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    num_elem=len(abc)

    #формирование id
    year=dat.year
    day=dat.julday
    time=dat.strftime("%H%M%S")

    id10=str(day)+time
    id10=int(id10)
    newid=[]
    while id10>=num_elem:
        indx=id10%num_elem
        newid.append(indx)
        id10=id10//num_elem

    if id10!=0:
        newid.append(id10)

    newid.reverse()
    id=code+str(year)+'-'

    for i in newid:
        id+=str(abc[i])

    return id

#декодирование Event ID обратно в дату
def decodeID(evtid):
    abc = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
           'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    num_elem = len(abc)
    s=evtid.split('-')
    year=s[0]
    year=int(year[len(year)-4:])
    id=s[1]
    n=len(id)-1
    sum=0
    for i in id:
        indx=abc.index(i)
        sum+=indx*num_elem**n
        n-=1
    sum=str(sum)
    jul=(sum[:3])
    h=(sum[3:5])
    m=(sum[5:7])
    sec=sum[7:9]
    res=str(year)+'-'+jul+'T'+h+':'+m+':'+sec
    dat=UTCDateTime(res)
    return dat

