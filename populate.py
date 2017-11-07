import os
import json
from models import *
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.create_all()


def to_entity(db, e):
    E = Entity(e['name'])
    ents = Entity.query.all()
    ids = {_.id for _ in ents}
    if e['id'] in ids:
        return None
    for k in e.keys():
        if k not in {'rank'} and e['id'] not in ids:
            E.__setattr__(k, e.get(k, None))
    return E


def add_edge(db, e):
    parent = Entity.query.filter(Entity.id == int(e['parent'])).all()
    child = Entity.query.filter(Entity.id == int(e['child'])).all()

    if len(parent) == 1 and len(child) == 1:

        parent = parent[0]
        child = child[0]
        try:
            edg = Edge(parent, child, int(e['share']), e['special'])
            return edg
        except IntegrityError:
            pass
    else:
        print('Error, non matching parents for ', e)


def add_all_edges(db, data):
    edges = data['shares']['children']
    i = 0
    Edges = []
    for _, children in edges.items():
        for edge in children:
            print('\r %d' % i, end='')
            edg = add_edge(db, edge)
            i += 1
            if edg:
                Edges.append(edg)
    db.session.object_session(edg).add_all(Edges)
    db.session.object_session(edg).commit()
    # edges = data['shares']['parents']
    # for _, children in edges.items():
    #     for edge in children:
    #         print('\r %d'%i, end='')
    #         add_edge(db, edge)
    #         i += 1


def get_json_data():
    with open('./static/data.min.json', 'r') as f:
        data = json.load(f)
    return data


def add_all_entities(db, data):
    ents = [v for k, v in data['entitys']['names'].items()]
    Ents = []
    for i, e in enumerate(ents):
        E = to_entity(db, e)
        if E:
            Ents.append(E)
        print('\r %d' % i, end='')
    db.session.add_all(Ents)


def delete_all_entities(db):
    ents = Entity.query.all()
    if len(ents) == 0:
        return
    s = db.session.object_session(ents[0])
    for e in ents:
        s.delete(e)
    if 'y' in 'Sure you want to delete ?':
        s.commit()
    else:
        s.rollback()


def delete_all_edges(db):
    edges = Edge.query.all()
    if len(edges) == 0:
        return
    s = db.session.object_session(edges[0])
    for e in edges:
        s.delete(e)
    if 'y' in input('Sure you want to delete ?  '):
        s.commit()
    else:
        s.rollback()


def delete_all(db):
    db.session.rollback()
    delete_all_edges(db)
    delete_all_entities(db)
    see(db)


def add_all(db):
    delete_all(db)
    data = get_json_data()
    print('data loaded')
    add_all_entities(db, data)
    db.session.commit()
    print()
    add_all_edges(db, data)
    db.session.commit()


def see(db):
    print('Edges: ', len(Edge.query.all()))
    print('Entities', len(Entity.query.all()))


def make_consistent(db):
    ents = Entity.query.all()
    for e in ents:
        if e.other_groups == '':
            e.other_groups = None
        if e.long_name == '':
            e.long_name = None
        if e.website == '':
            e.website == None
        if e.wiki == None:
            e.wiki = None
        db.session.object_session(e).commit()
    edges = Edge.query.all()
    for ed in edges:
        if ed.special == '':
            ed.special = None
            db.session.object_session(ed).commit()



if __name__ == "__main__":
    see(db)
    if 'y' in input('drop all?'):
        db.drop_all()
    if 'y' in input('add and delete?'):
        add_all(db)
        see(db)
    if 'y' in input('Make consistent?'):
        make_consistent(db)
