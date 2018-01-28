import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from werkzeug import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.from_object(__name__) # load config from this file , flaskr.py

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'myssbm.db'),
    SECRET_KEY='devkey',
))
app.config.from_envvar('MYSSBM_SETTINGS', silent=True)

#connect to database
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

#initialize database
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db()

#opens database connection if there isn't already one
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

#execute a query to the database
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv #return only first element if one is true

#close the database
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

#home page that displays user data
@app.route('/')
def show_data():
    if session.get('logged_in') != None: #display info and use show_data template if logged in
        db = get_db()
        user = query_db('select tag, main from users where tag = ?', [session['tag']],one=True)
        sets1 = query_db('select wins_1, wins_2, tag_2, char_1, char_2, tournament from sets where tag_1 = ?', [user['tag']],one=False) #where player is tag 1
        sets2 = query_db('select wins_1, wins_2, tag_1, char_1, char_2, tournament from sets where tag_2 = ?', [user['tag']],one=False) #where player is tag 2
        placings = query_db('select placing, tournament from placings where tag = ?', [user['tag']], one=False)
        return render_template('show_data.html', user=user, sets1=sets1, sets2=sets2, placings = placings)
    else: #return default template
        return render_template('layout.html')

#register route
@app.route('/register', methods=['GET','POST'])
def register():
    error = None
    if request.method == 'POST':
        existing_users = query_db('select tag from users', '',one=False)
        if request.form['tag'] in existing_users: #if username is taken
            error = 'That tag is already registered'
        else:  #go through with insert
            db = get_db()
            db.execute('insert into users (email, password, tag, main) values (?, ?, ?, ?)',
                    [request.form['email'],
                    generate_password_hash(request.form['password']),
                    request.form['tag'], request.form['main']] )
            db.commit()
            flash('Successfully registered')
            return redirect(url_for('show_data'))
    return render_template('register.html', error=error)

#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = query_db('''select * from users where
            tag = ?''', [request.form['tag']], one=True)
        if user is None:
            error = 'Invalid tag'
        elif not check_password_hash(user['password'], request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['logged_in'] = True
            session['tag'] =  user['tag']
            return redirect(url_for('show_data'))

    return render_template('login.html', error=error)

#end sessions
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('tag', None)
    flash('You were logged out')
    return redirect(url_for('show_data'))

#add a set
@app.route('/addset', methods=['POST'])
def addset():
    if request.method == 'POST':
        db = get_db()
        db.execute('insert into sets (tag_1, tag_2, wins_1, wins_2, char_1, char_2, tournament) values (?, ?, ?, ?, ?, ?, ?)',
                    [session['tag'], request.form['opp_tag'], request.form['games_won'], request.form['games_lost'],
                    request.form['my_char'], request.form['opp_char'], request.form['set_tournament']])
        db.commit()
        flash('Successfully added set!')
    return redirect('/')

#add placing
@app.route('/addplacing', methods=['POST'])
def addplacing():
    if request.method == 'POST':
        db = get_db()
        db.execute('insert into placings (placing, tournament, tag) values (?, ?, ?)',
        [request.form['placing'], request.form['placing_tournament'], session['tag']])
        db.commit()
        return redirect('/')
