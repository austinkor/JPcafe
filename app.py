import flask
import sqlite3
from datetime import datetime

conn = sqlite3.connect('menu.db')

app = flask.Flask(__name__)

@app.route('/')
def home():
    temp = []

    cursor = conn.execute('SELECT * FROM inventory')
    for row in cursor:
        temp_arr = []
        for item in row:
            temp_arr += [item]
        temp += [temp_arr]
    #temp is a list of list
    #each list itemid,store,foodname,price,quantity,image
    for times in range(len(temp)):
        temp[times][3] = '$' + str(float(temp[times][3]))
        temp[times][4] = str(temp[times][4]) + 'avail'
    
    return flask.render_template('home.html',food = temp)

@app.route('/order/',methods = ['GET','POST'])
def order():
    entry = flask.request.form
    ordered_key = []
    arr = []
    total = 0

    for times in range(1,11):
        key = str(times)
        cursor = conn.execute('SELECT quan FROM inventory WHERE itemID = ?',(times,))
        for item in cursor:
            quan = item[0]
        if entry[key] != '':
            if int(entry[key]) > quan:
                return flask.redirect(flask.url_for('failed'))
            ordered_key += [key]
            
    if entry['member'] == 'Member login and Order':
        cursor = conn.execute('SELECT memEmail FROM member')
        valid = []
        discount = True
        for item in cursor:
            valid += [item[0]]
        if entry['email'] not in valid:
            return flask.redirect(flask.url_for('failed'))
        
        cursor = conn.execute('SELECT password FROM member WHERE memEmail = ?',(entry['email'],))
        for item in cursor:
            correct = item[0]
        
        if entry['password'] != correct:
            return flask.redirect(flask.url_for('failed'))

        cursor = conn.execute('SELECT memName FROM member WHERE memEmail = ?',(entry['email'],))
        for item in cursor:
            name = item[0]
    else:
        name = entry['name']
        discount = False

    for item in ordered_key:
        cursor = conn.execute('SELECT itemName,price FROM inventory WHERE itemID = ?',(item,))
        for row in cursor:
            temp = [row[0]] + [row[1]] + [int(entry[item])]
            arr += [temp]
            total += (int(entry[item])) * row[1]

    temp = str(datetime.now())
    date,time = temp.split(' ')
    
    if discount:
        pay = total * 0.9
        conn.execute('INSERT INTO "order"(customerName,date,isMem,totalpayable) VALUES(?,?,?,?)',(name,date,1,pay))
    else:
        pay = total
        conn.execute('INSERT INTO "order"(customerName,date,isMem,totalpayable) VALUES(?,?,?,?)',(name,date,0,pay))

    cursor = conn.execute('SELECT orderID FROM "order"')
    for item in cursor:
        orderid = item[0]

    for item in ordered_key:
        conn.execute('INSERT INTO itemOrdered VALUES(?,?,?)',(orderid,item,entry[item]))

    for times in range(1,11):
        key = str(times)
        cursor = conn.execute('SELECT quan FROM inventory WHERE itemID = ?',(times,))
        for item in cursor:
            quan = item[0]
        if entry[key] != '':
            conn.execute('UPDATE inventory SET quan = ? WHERE itemID = ?',(quan-int(entry[key]),times))
    
    conn.commit()
    return flask.render_template('order.html',name=name,arr=arr,discount=discount,total=total,pay=pay,date=date)

@app.route('/register/',methods = ['GET','POST'])
def signuppage():
    return flask.render_template('signup.html')

@app.route('/registerconfirm/',methods = ['GET','POST'])
def create():
    entry = flask.request.form
    cursor = conn.execute('SELECT memEmail FROM member')

    arr = []
    for row in cursor:
        arr += [row[0]]

    if entry['signemail'] not in arr and entry['signname'] != '' and entry['signpass'] != '':
        conn.execute('INSERT INTO member '+
                     'VALUES(?,?,?)',(entry['signname'],entry['signemail'],entry['signpass']))
        conn.commit()
        
        return flask.render_template('create.html')
    else:
        return flask.render_template('failedcreate.html')

@app.route('/unsuccessful/',methods = ['GET','POST'])
def failed():
    

    return flask.render_template('failed.html')

if __name__ == '__main__':
    app.run(port=5445)
