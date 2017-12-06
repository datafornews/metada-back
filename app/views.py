from app import app
from app import imageNetUsernames
from app.models.Graph_model import *
from flask import render_template, jsonify, abort
import datetime


def clear_instance(model_instance):
    dic = model_instance.__dict__.copy()
    keys_to_delete = {
        '_sa_instance_state',
        'created_by_id',
        'created_at',
        'updated_by_id',
        'updated_at'
    }
    ks = set(dic.keys())
    for k in ks.intersection(keys_to_delete):
        del dic[k]
    return dic


def entity_to_dict(en):
    dic = clear_instance(en)
    dic['category'] = dic['category'].code
    if dic['website']:
        dic['website'] = dic['website']
    if en.wiki:
        dic['wiki'] = wiki_data_to_dict(en.wiki)

    return dic


def wiki_data_to_dict(wd):
    return {
        'lang': wd.lang,
        'title': wd.title
    }


def edge_to_dict(ed):
    return clear_instance(ed)


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/db_meta_data')
def get_db_meta_data():
    metadata = DBMetaData.query.all()
    if metadata:
        metadata = metadata[0].__dict__.copy()
        del metadata['_sa_instance_state']
    else:
        metadata = None
    return jsonify(metadata)


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


@app.route('/data/')
def get_full_data():

    ents = Entity.query.all()
    edges = Edge.query.all()

    return jsonify({
        'entities': [entity_to_dict(e) for e in ents if not e.blacklist],
        'shares': [edge_to_dict(e) for e in edges if not e.blacklist]
    })


@app.route('/update/<timestamp>')
def get_update(timestamp):
    try:
        ts = int(timestamp)
        if ts >= 0:
            dts = datetime.datetime.fromtimestamp(ts)
            ents = Entity.query.filter(Entity.updated_at > dts).all()
            edges = Edge.query.filter(Edge.updated_at > dts).all()

            return jsonify({
                'entities': [entity_to_dict(e) for e in ents],
                'shares': [edge_to_dict(e) for e in edges]
            })
        else:
            abort(404)
    except (ValueError, TypeError) as e:
        print(e)
        abort(404)
