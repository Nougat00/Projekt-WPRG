import datetime
import sqlite3
from flask import Flask, render_template, url_for, redirect, g, request, session

app = Flask(__name__)

app.secret_key='uijaojikutassdnao'

DATABASE = 'C:/Users/barte/Documents/PJAKT/OneDrive - Polsko-Japońska Akademia Technik Komputerowych/WPRG/Projekt-WPRG/identifier.sqlite'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def hello_world():
    return redirect(url_for('login'))

@app.route('/choice', methods=('GET', 'POST'))
def choice():
    return render_template('choice.html', user=session['user_name'])


@app.route('/costs', methods=('GET', 'POST'))
def costs():
    if request.method == 'POST':
        spend_name = request.form['spendName']
        spend_type=request.form['spendType']
        spend_value=request.form['spendValue']
        database=get_db()
        new_spend=database.execute("Insert into costs(name, categry, value, id_user) values (?,?,?,?)", (spend_name, spend_type, spend_value, session['id_user']))
        database.commit()
        new_spend.close()
    return render_template('costs.html')

@app.route('/salary', methods=('GET', 'POST'))
def salary():
    if request.method == 'POST':
        salary_value = request.form['salaryValue']
        print(type(salary_value))
        database = get_db()
        salary_post=database.execute("Update table_name set salary=? where id_user=?", (salary_value, session['id_user']))
        database.commit()
        salary_post.close()
    return render_template('salary.html')

@app.route('/sumary', methods=('GET', 'POST'))
def sumary():

    tmp = []
    suma = 0
    salary=0
    foodvalue=0
    livevalue=0
    servicesvalue=0
    stealvalue=0

    from_user = query_db("Select salary from table_name")
    food = query_db("Select value from costs where id_user=? and categry=?", (session['id_user'], 'food'))
    live = query_db("Select value from costs where id_user=? and categry=?", (session['id_user'], 'live'))
    services = query_db("Select value from costs where id_user=? and categry=?", (session['id_user'], 'services'))
    steal = query_db("Select value from costs where id_user=? and categry=?", (session['id_user'], 'steal'))

    for x in from_user:
        salary = sum(x)
    for x in food:
        foodvalue+=sum(x)
    for x in live:
        livevalue+=sum(x)
    for x in services:
        servicesvalue+=sum(x)
    for x in steal:
        stealvalue+=sum(x)
    suma=foodvalue+livevalue+servicesvalue+stealvalue
    procentfood=round(((float(foodvalue)/float(suma))*100), 2)
    procentlive=round(((float(livevalue)/float(suma))*100), 2)
    procentservices=round(((float(servicesvalue)/float(suma))*100), 2)
    procentsteal=round(((float(stealvalue)/float(suma))*100), 2)
    salary_pro=round(((float(suma)/float(salary))*100),2)
    if request.method == 'POST':
        spend_type = request.form['spendType']
        from_costs = query_db("Select name, value from costs where id_user=? and categry=?", (session['id_user'], spend_type))
        for x in from_costs:
            tmp.append(x)
            suma+=x[1]
    return render_template('sumary.html', zarobki=salary, procent_zarob=salary_pro,  result_db=tmp, suma_food=foodvalue, suma_live=livevalue, suma_serv=servicesvalue, suma_steal=stealvalue, p1=procentfood, p2=procentlive, p3=procentservices, p4=procentsteal)

@app.route('/register', methods=('GET', 'POST'))
def register():
    mess=""
    if request.method == 'POST':
        user_name = request.form['username']
        user_password = request.form['password']
        database = get_db()
        from_db = query_db("Select id_user, login, password from table_name where login=?", (user_name,))
        if from_db and from_db[0][1] == user_name:
            mess="Użytkownik o takim loginie już istnieje! Wybierz inny login"
        else:
            new_spend = database.execute("Insert into table_name(login, password) values (?,?)",(user_name, user_password))
            database.commit()
            new_spend.close()
            mess="O dziwo udało ci się zarejestrować. Gratulacje!"
    return render_template('register.html', text=mess)

@app.route('/login', methods=('GET', 'POST'))
def login():
    mess=""
    if request.method == 'POST':
        session.pop('user_name', None)
        user_name = request.form['username']
        user_password = request.form['password']
        from_db=query_db("Select id_user, login, password from table_name where login=?",(user_name,))
        if from_db and from_db[0][2] == user_password:
            session['id_user'] = from_db[0][0]
            session['user_name'] = from_db[0][1]
            session['timestamp'] =datetime.datetime.now()
            return redirect(url_for('choice'))
        else:
            mess="Zły login lub hasło"
    return render_template('login.html', message=mess)


if __name__ == '__main__':
    app.run()