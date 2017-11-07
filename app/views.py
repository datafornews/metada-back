from app import app
from app.graph_models import *
from flask import render_template, jsonify

@app.route('/')
def hello():
    return "Hello World!"


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


@app.route('/react/')
def render_react():
    return render_template('index.html')


@app.route('/data/')
def get_full_data():

    def entity_to_dict(en):
        dic = en.__dict__.copy()
        del dic['_sa_instance_state']
        dic['category'] = dic['category'].code
        if dic['website']:
            dic['website'] = dic['website']
        if dic['wiki']:
            dic['wiki'] = dic['wiki']
        return dic

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