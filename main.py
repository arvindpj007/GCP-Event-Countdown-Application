from datetime import timedelta
from flask import Flask, jsonify, request, session, redirect, url_for
from flask_session import Session
from google.cloud import datastore
import os
import bcrypt

app = Flask(__name__, static_url_path='')
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=60)

DS = datastore.Client(project='countdown-252800')
EVENT = 'Event'  # Name of the event table, can be anything you like.
ROOT = DS.key('Entities', 'root')  # Name of root key, can be anything.
USER = 'User'


@app.route('/')
def index():
    """ This is the default page.
        get:
            summary: / endpoint.
            description: renders static file index.html.
            responses:
                200:
                    description: The events list and the option to add a new event.
        """
    if check_session():
        # migrate_events()
        return app.send_static_file('index.html')
    else:
        return redirect('login.html', 302)

    # return app.send_static_file('index.html')


@app.route('/events')
def events():
    """ Returns all the events from cloudstore.
        get:
            summary: events endpoint.
            description: Gets all the event entities and returns them as json .
            responses:
                200:
                    description: json object to be returned.
                    schema: [{name:"",date:""}]
                404:
                    description: Error : null.
        """
    if check_session():
        user = session['username']
        key_space = DS.key('User', user)
        query = DS.query(kind=EVENT, ancestor=key_space).fetch()
        event_list = []
        for val in query:
            event_list.append(dict(name=val.get('name'), date=val.get('date')))
        # print(len(event_list))
        return jsonify(events=event_list)
    else:
        return redirect('/loginPage', 302)


@app.route('/event', methods=['POST'])
def event():
    """ To push events to cloud store
        get:
            summary: event endpoint.
            description: Get name and date through ajax and stores it as an entity in cloud store and returns ID.
            parameters:
                - name: name
                  in: request
                  description: Event Name
                  type: string
                  required: true
                  - name: date
                    in: request
                    description: Event ETA
                    type: string
                    required: true
            responses:
                200:
                    description: Event ID to be returned.
                    schema: string
        """
    if check_session():
        para = request.data.decode('UTF-8').split()
        name = para[0]
        r_date = para[1]
        print(r_date)
        [y, m, d] = r_date.split('-')
        date = d + '-' + m + '-' + y
        x = put_event(name, date)
        return str(x)
    else:
        return redirect(url_for('login_page'), 302)


@app.route('/delete', methods=['POST'])
def delete():
    """ To implicitly delete events from cloud store
            get:
                summary: delete endpoint.
                description: Get name and date through ajax and use it to delete the event from cloud store.
                parameters:
                    - name: name
                      in: request
                      description: Event Name
                      type: string
                      required: true
                      - name: date
                        in: request
                        description: Event ETA
                        type: string
                        required: true
                responses:
                    200:
                        description: Event will bbe deleted from cloud store.
            """
    if check_session():
        para2 = request.get_data().decode('UTF-8').split()
        name = para2[1]
        r_date = para2[0]
        delete_event(name, r_date)
        return "1"
    else:
        return redirect(url_for('login_page'), 302)


@app.route('/loginPage')
def login_page():
    return app.send_static_file('login.html')


@app.route('/username')
def get_username():
    if check_session():
        return jsonify(name=session['username'])
    else:
        return ' '


@app.route('/logoutUser')
def logout_user():
    session.pop('username', None)
    return '1'


@app.route('/loginUser', methods=['POST'])
def login_user():
    try:
        para = request.get_data().decode('UTF-8').split()
        username = para[0]
        password = para[1]
        fetch_password = None
        b_password = password.encode('UTF-8')
        # print(username, password)
        query = DS.query(kind=USER)
        query.add_filter('username', '=', username)
        next_entity = query.fetch()

        for val in next_entity:
            fetch_password = val['password']

        if fetch_password is None:
            print('no such user')
            return '0'
        else:
            fetch_hash = fetch_password.encode('UTF-8')
            if bcrypt.checkpw(b_password, fetch_hash):
                print('correct')
                session['username'] = username
                return redirect(url_for('index'), 302)
            else:
                print('incorrect password')
                return '0'

    except Exception as e:
        print(e)

    return '1'


@app.route('/registerUser', methods=['POST'])
def register_user():
    # try:
    para = request.get_data().decode('UTF-8').split()
    username = para[0]
    password = para[1]
    b_password = password.encode('UTF-8')
    hashed = bcrypt.hashpw(b_password, bcrypt.gensalt())
    s_hashed = str(hashed.decode('UTF-8'))
    entity = datastore.Entity(key=DS.key('User'))
    entity.update({'username': username, 'password': s_hashed})
    DS.put(entity)
    session['username'] = username

    return '1'


def check_session():
    if 'username' in session:
        return True
    else:
        return False


def put_event(name, date_str):
    """Put the event into the cloud store using the given parameters name and date"""
    # print('putting')
    user = session['username']
    key_space = DS.key('User', user)
    key = DS.key(EVENT, parent=key_space)
    entity = datastore.Entity(key=key)
    entity.update({'name': name, 'date': date_str})
    DS.put(entity)
    return id(DS.key)


def delete_event(name, date):
    """Delete the event into the cloud store using the given parameters name and date"""
    user = session['username']
    key_space = DS.key('User', user)
    query = DS.query(kind=EVENT, ancestor=key_space)
    query.add_filter('name', '=', name)
    query.add_filter('date', '=', date)
    next_entity = query.fetch()
    for val in next_entity:
        DS.delete(val.key)


if __name__ == '__main__':
    """Run the app"""
    app.run()


def delete_migrate_events():
    query = DS.query(kind=EVENT, ancestor=ROOT).fetch()
    for val in query:
        DS.delete(val.key)


def migrate_events():
    query = DS.query(kind=EVENT, ancestor=ROOT).fetch()
    key_space = DS.key('User', 'user1')
    key = DS.key(EVENT, parent=key_space)
    for val in query:
        print(val)
        entity = datastore.Entity(key=key)
        entity.update({'name': val['name'], 'date': val['date']})
        DS.put(entity)
        DS.delete(val.key)

# def fetch_events():
#     print('fetching')
#     query = DS.query(kind=EVENT, ancestor=ROOT).fetch()
#     event_list = []
#     for val in query:
#         event_list.append(dict(name=val.get('name'), date=val.get('date').date()))
#     print(event_list)
