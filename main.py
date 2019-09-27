import urllib
import uuid
from datetime import timedelta, datetime, timezone
from flask import Flask, jsonify, request, session, redirect, url_for
import logging
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
SESSION = 'Session'


@app.route('/')
def index():
    """ This is the default page.
        get:
            summary: / endpoint.
            description: renders static file index.html if session is available.
            responses:
                200:
                    description: The events list and the option to add a new event.
                302:
                   description: Redirect to login page.
    """

    username = get_user()

    print('loading index')

    if not username:
        # migrate_events()
        return redirect(url_for('login_page'))
    else:
        return app.send_static_file('index.html')

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
    username = get_user()

    if username:
        try:
            user = username
            key_space = DS.key('User', user)
            query = DS.query(kind=EVENT, ancestor=key_space).fetch()
            event_list = []
            for val in query:
                event_list.append(dict(name=val.get('name'), date=val.get('date')))
            # print(len(event_list))
            print('why redirect?')
            return jsonify(events=event_list)

        except Exception as e:
            print(e)
    else:
        print('redirect')
        return redirect(url_for('login_page'))

    print('no redirect')

    return 'events=""'
    # else:
    #     return redirect('/loginPage', 302)


@app.route('/event', methods=['POST'])
def event():
    """ To push events to cloud store
        get:
            summary: event endpoint.
            description: Get name and date and stores it as an entity in cloud store and returns ID.
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
    username = get_user()

    if username:
        para = request.data.decode('UTF-8').split()
        name = para[0]
        r_date = para[1]
        print(r_date)
        [y, m, d] = r_date.split('-')
        date = d + '-' + m + '-' + y
        x = put_event(username, name, date)
        return str(x)
    else:
        return redirect(url_for('login_page'), 302)


@app.route('/delete', methods=['POST'])
def delete():
    """ To  delete events from cloud datastore
        post:
            summary: delete endpoint.
            description: Get name and date and use it to delete the event from cloud store.
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
                    description: Event will be deleted from cloud store.
    """
    username = get_user()
    if username:
        para2 = request.get_data().decode('UTF-8').split()
        name = para2[1]
        r_date = para2[0]
        delete_event(username, name, r_date)
        return "1"
    else:
        return redirect(url_for('login_page'), 302)


@app.route('/loginPage', methods=['GET'])
def login_page():
    """ This is the login page
            get:
                summary: login and register page.
                description: Renders the login/register page.
                responses:
                    200:
                        description: Login Page will be rendered
    """
    return app.send_static_file('login.html')


# @app.route('/username')
# def get_username():
#     if check_session():
#         return jsonify(name=session['username'])
#     else:
#         return redirect(url_for('login_page'), 302)


@app.route('/logoutUser')
def logout_user():
    """ This is to logout user, or remove session.
            get:
                summary: deletes the session cookie to logout user.
                description: deletes the session cookie.
                responses:
                    200:
                        description: User will be logged out and session will be removed.
    """
    print('logout start')
    session_cookie = check_session()
    session_key = DS.key(SESSION, session_cookie)
    session_now = DS.get(session_key)

    if session_now:
        DS.delete(session_key)

    resp = redirect('/')
    resp.set_cookie('user', expires=0)

    print('logout finish')
    return resp


@app.route('/loginUser', methods=['POST'])
def login_user():
    """ To verify users
            get:
                summary: loginUser endpoint.
                description: Get name and date and redirects to index.html upon password verification by setting an active session cookie.
                parameters:
                    - name: username
                      in: request
                      description: Username
                      type: string
                      required: true
                      - name: password
                        in: request
                        description: User password
                        type: string
                        required: true
                responses:
                    200:
                        description: incorrect username or password.
                    302:
                        description: redirects to index.html.

    """
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

        session_cookie = check_session()
        if session_cookie:
            session_key = DS.key(SESSION, session_cookie)
            session_now = DS.get(session_key)

            if session_now:
                print('delete old session')
                DS.delete(session_key)

        if fetch_password is None:
            print('no such user')
            params = urllib.parse.urlencode({'error': 'User {} or password incorrect'.format(username)})
            resp = redirect('/loginUser?' + params)
            resp.set_cookie('user', expires=0)
            return resp

        else:
            fetch_hash = fetch_password.encode('UTF-8')
            if bcrypt.checkpw(b_password, fetch_hash):
                print('correct')
                session_token = str(uuid.uuid4())
                new_session = datastore.Entity(key=DS.key(SESSION, session_token))
                new_session.update({
                    'token': session_token,
                    'username': username,
                    'expire': now() + timedelta(hours=1)
                })
                print('put new session'+session_token+username)
                DS.put(new_session)
                resp = redirect('/')
                resp.set_cookie('user', session_token, max_age=3600)
                print('login finish')
                return resp

            else:
                print('incorrect password')
                params = urllib.parse.urlencode({'error': 'User {} or password incorrect'.format(username)})
                resp = redirect('/loginUser?' + params)
                resp.set_cookie('user', expires=0)
                return resp

    except Exception as e:
        print(e)

    return resp


@app.route('/registerUser', methods=['POST'])
def register_user():
    """ To verify users
            get:
                summary: registeUser endpoint.
                description: Get name and date and adds User to cloud datastore followed by setting an active session cookie.
                parameters:
                    - name: username
                      in: request
                      description: Username
                      type: string
                      required: true
                      - name: password
                        in: request
                        description: User password
                        type: string
                        required: true
                responses:
                    200:
                        description: register user confirmation.
    """
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

    session_token = str(uuid.uuid4())
    new_session = datastore.Entity(key=DS.key(SESSION, session_token))
    new_session.update({
        'token': session_token,
        'username': username,
        'expire': now() + timedelta(hours=1)
    })
    DS.put(new_session)
    resp = redirect('/')
    resp.set_cookie('user', session_token, max_age=3600)
    return resp


def now():
    return datetime.now(timezone.utc)


def check_session():
    """Check session availability"""
    print('checking session')
    session_cookie = request.cookies.get('user')
    if not session_cookie:
        print('no session cookie')
        return None

    print('session cookie present')
    return session_cookie
    # if 'username' in session:
    #     return True
    # else:
    #     return False


def get_user():
    print('getting user')
    session_cookie = check_session()

    if not session_cookie:
        print('no session cookie in get user')
        return None

    else:
        print('session cookie present in get user')
        session_key = DS.key(SESSION, session_cookie)
        session_now = DS.get(session_key)

        if not session_now:
            print('session not in database')
            return None

        expire_time = session_now['expire']

        if expire_time < now():
            DS.delete(session_key)
            print('session expired')
            return None

        query = DS.query(kind=USER)
        query.add_filter('username', '=', session_now['username'])
        next_entity = query.fetch()
        for val in next_entity:
            if not val:
                DS.delete(session_key)
                print('No such user for session')
                return None

        return session_now['username']


def put_event(username, name, date_str):
    """Put the event into the cloud store using the given parameters name and date"""
    # print('putting')
    user = username
    key_space = DS.key('User', user)
    key = DS.key(EVENT, parent=key_space)
    entity = datastore.Entity(key=key)
    entity.update({'name': name, 'date': date_str})
    DS.put(entity)
    return id(DS.key)


def delete_event(username, name, date):
    """Delete the event into the cloud store using the given parameters name and date"""
    user = username
    key_space = DS.key('User', user)
    query = DS.query(kind=EVENT, ancestor=key_space)
    query.add_filter('name', '=', name)
    query.add_filter('date', '=', date)
    next_entity = query.fetch()
    for val in next_entity:
        DS.delete(val.key)


if __name__ == '__main__':
    """Run the app"""
    app.run(debug=True)


def migrate_events():
    """Migrate the data to the first registered user"""
    query = DS.query(kind=EVENT, ancestor=ROOT).fetch()
    user = session['username']
    key_space = DS.key('User', user)
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
