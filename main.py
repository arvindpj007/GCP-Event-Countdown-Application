from flask import Flask, jsonify, request, session, redirect, url_for
from google.cloud import datastore
import os
import bcrypt

app = Flask(__name__, static_url_path='')
app.secret_key = os.urandom(24)

DS = datastore.Client(project='countdown-252800')
EVENT = 'Event'  # Name of the event table, can be anything you like.
ROOT = DS.key('Entities', 'root')  # Name of root key, can be anything.
USER = 'User'


@app.route('/')
def hello_world():
    """ This is the default page.
        get:
            summary: / endpoint.
            description: renders static file index.html.
            responses:
                200:
                    description: The events list and the option to add a new event.
        """
    return app.send_static_file('login.html')


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
    query = DS.query(kind=EVENT, ancestor=ROOT).fetch()
    event_list = []
    for val in query:
        event_list.append(dict(name=val.get('name'), date=val.get('date')))
    # print(len(event_list))
    return jsonify(events=event_list)


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
    para = request.data.decode('UTF-8').split()
    name = para[0]
    r_date = para[1]
    print(r_date)
    [y, m, d] = r_date.split('-')
    date = d + '-' + m + '-' + y
    x = put_event(name, date)
    return str(x)


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
    para2 = request.get_data().decode('UTF-8').split()
    name = para2[1]
    r_date = para2[0]
    delete_event(name, r_date)
    return "1"


@app.route('/loginUser', methods=['POST'])
def login_user():
    try:
        para = request.get_data().decode('UTF-8').split()
        username = para[0]
        password = para[1]
        fetch_password = None
        b_password = password.encode('UTF-8')
        print(username, password)
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
            else:
                print('incorrect password')
                return '0'

    except Exception as e:
        print(e)

    return '1'


@app.route('/update_session')
def update_session():
    return redirect('/events', 302)


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
    # print(username, password)
    # except Exception as e:
    #     print(e)
    return '1'


def put_event(name, date_str):
    """Put the event into the cloud store using the given parameters name and date"""
    # print('putting')
    key = DS.key(EVENT, parent=ROOT)
    entity = datastore.Entity(key=key)
    entity.update({'name': name, 'date': date_str})
    DS.put(entity)
    return id(DS.key)


def delete_event(name, date):
    """Delete the event into the cloud store using the given parameters name and date"""
    query = DS.query(kind=EVENT, ancestor=ROOT)
    query.add_filter('name', '=', name)
    query.add_filter('date', '=', date)
    next_entity = query.fetch()
    for val in next_entity:
        DS.delete(val.key)


if __name__ == '__main__':
    """Run the app"""
    app.run()


def migrate_events():
    query = DS.query(kind=EVENT, ancestor=ROOT).fetch()
    user_root = DS.key('User','user1')
    key = DS.key(EVENT, user_root)
    entity = datastore.entity(key=key)
    for val in query:
        entity.update(val)

# def fetch_events():
#     print('fetching')
#     query = DS.query(kind=EVENT, ancestor=ROOT).fetch()
#     event_list = []
#     for val in query:
#         event_list.append(dict(name=val.get('name'), date=val.get('date').date()))
#     print(event_list)
