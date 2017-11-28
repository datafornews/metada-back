from app import app
from app.models.Graph_model import *
from flask import render_template, jsonify


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/db_meta_data')
def get_db_meta_data():
    metadata = DBMetaData.query.all()
    if len(metadata) > 0:
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

    def entity_to_dict(en):
        dic = en.__dict__.copy()
        del dic['_sa_instance_state']
        dic['category'] = dic['category'].code
        if dic['website']:
            dic['website'] = dic['website']
        if en.wiki:
            dic['wiki'] = wiki_data_to_dict(en.wiki)
        ks = set(dic.keys())
        for k in ks.intersection({'created_by_id', 'created_at', 'updated_by_id', 'updated_at'}):
            del dic[k]
        return dic

    def wiki_data_to_dict(wd):
        return {
            'lang': wd.lang,
            'title': wd.title
        }

    def edge_to_dict(ed):
        dic = ed.__dict__.copy()
        del dic['_sa_instance_state']
        return dic

    ents = Entity.query.all()
    edges = Edge.query.all()

    return jsonify({
        'entities': [entity_to_dict(e) for e in ents],
        'shares': [edge_to_dict(e) for e in edges]
    })
