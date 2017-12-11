import random
import datetime
from app import app
from app.models.Graph_model import *
from app.models.User_model import *
from app.utils.jwt import get_jwt_user
from app.utils.models_to_dict import user_to_dict, entity_to_dict, edge_to_dict
from flask import jsonify, abort, request, Response, make_response


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


@app.route('/random_username')
def get_random_username():
    from app import imageNetUsernames
    rd_un = random.sample(imageNetUsernames, 1)[0]

    while User.query.filter(User.username == rd_un).all():
        rd_un = random.sample(imageNetUsernames, 1)[0]

    return jsonify({
        'username': rd_un
    })


@app.route('/verify/<link>')
def verify_account(link):
    vf = VerifiedEmail.query.filter(VerifiedEmail.link == link).first()
    now = datetime.datetime.utcnow()
    if vf and now - vf.created_at < datetime.timedelta(days=100):
        vf.user.confirmed_at = now
        vf.user.active = True
        db.object_session(vf).delete(vf)
        db.object_session(vf).commit()
        return jsonify({
            'verified': True
        })
    return abort(404)


@app.route('/data/')
def get_full_data():

    ents = Entity.query.filter_by(
        blacklist=False).filter_by(candidate=False).all()
    edges = Edge.query.filter_by(
        blacklist=False).filter_by(candidate=False).all()

    return jsonify({
        'entities': [entity_to_dict(e) for e in ents],
        'shares': [edge_to_dict(e) for e in edges]
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


@app.route('/user_exists/<username>')
def user_exists(username):
    return jsonify({
        'exists': User.query.filter_by(username=username).first() is not None
    })


@app.route('/email_exists/<email>')
def email_exists(email):
    return jsonify({
        'exists': User.query.filter_by(email=email).first() is not None
    })


@app.route('/a/<b>')
def a(b):
    result = get_jwt_user(request)
    if not result['allow']:
        return make_response(jsonify(result['response'])), 401

    user = result['response']
    if not user:
        return make_response(jsonify({'status': 'fail', 'message': 'noUser'})), 401
    return make_response(jsonify({'user': user_to_dict(user), 'b': b})), 200


@app.route('/<name>')
def hello_name(name):
    abort(Response(
        "Welcome at {}! <br/> Unfortunately there is nothing here :( (yet!)"
        .format(name)))
