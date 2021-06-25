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
    return render_template('choice.html')


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
    tmp_2=[]
    suma = 0
    procent=0
    if request.method == 'POST':
        spend_type = request.form['spendType']
        from_costs = query_db("Select name, value from costs where id_user=? and categry=?", (session['id_user'], spend_type))
        for x in from_costs:
            tmp.append(x)
            suma+=x[1]
        from_user= query_db("Select salary from table_name")
        for x in from_user:
            procent=sum(x)
        procent=round(((float(suma)/float(procent))*100),2)
    return render_template('sumary.html', result_db=tmp, suma_db=suma, procent_kw=procent)


@app.route('/login', methods=('GET', 'POST'))
def login():
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
    return render_template('login.html')


if __name__ == '__main__':
    app.run()
