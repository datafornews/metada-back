import random
import datetime
from flask import Blueprint, request, make_response, jsonify, abort, Response
from flask.views import MethodView

<<<<<<< HEAD
=======

>>>>>>> 992afbcd411a29a14ac37b0585f9a511767535b7
from app import bcrypt, db
from app.models.User_model import User
from app.models.Graph_model import Edge, Entity, WikiData, DBMetaData
from app.utils.models_to_dict import entity_to_dict, edge_to_dict
from flask_cors import CORS

public_blueprint = Blueprint('public', __name__)
CORS(public_blueprint, resources=r'/public/*')


class Hello(MethodView):

    def get(self):
        return "Hello World!"


class DBMetaDataAPI(MethodView):

    def get(self):
        metadata = DBMetaData.query.all()
        if metadata:
            metadata = metadata[0].__dict__.copy()
            del metadata['_sa_instance_state']
        else:
            metadata = None
        return jsonify(metadata)


class RandomUserName(MethodView):

    def get(self):
        from app import imageNetUsernames
        rd_un = random.sample(imageNetUsernames, 1)[0]

        while User.query.filter(User.username == rd_un).all():
            rd_un = random.sample(imageNetUsernames, 1)[0]

        return jsonify({
            'username': rd_un
        })


class FullData(MethodView):

    def get(self):
        # ents = Entity.query.filter_by(
        #     blacklist=False).filter_by(candidate=False).all()
        # edges = Edge.query.filter_by(
        #     blacklist=False).filter_by(candidate=False).all()
        # candidacy has yet to be implemented

        ents = Entity.query.filter_by(
            blacklist=False).all()
        edges = Edge.query.filter_by(
            blacklist=False).all()

        return jsonify({
            'entities': [entity_to_dict(e) for e in ents],
            'shares': [edge_to_dict(e) for e in edges]
        })


class UpdateData(MethodView):

    def get(self):
        timestamp = request.args.get('timestamp')
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


class UsernameExists(MethodView):

    def get(self):
        username = request.args.get('username')
        return jsonify({
<<<<<<< HEAD
            'exists': username and User.query.filter_by(
=======
            'exists': User.query.filter_by(
>>>>>>> 992afbcd411a29a14ac37b0585f9a511767535b7
                username=username).first() is not None
        })


class EmailExists(MethodView):

    def get(self):
        email = request.args.get('email')
        return jsonify({
<<<<<<< HEAD
            'exists': email and User.query.filter_by(email=email).first() is not None
=======
            'exists': User.query.filter_by(email=email).first() is not None
>>>>>>> 992afbcd411a29a14ac37b0585f9a511767535b7
        })


hello_view = Hello.as_view('hello_api')
db_meta_data_view = DBMetaDataAPI.as_view('db_meta_data_api')
random_username_view = RandomUserName.as_view('random_username_api')
full_data_view = FullData.as_view('full_data_api')
update_data_view = UpdateData.as_view('update_data_api')
username_exists_view = UsernameExists.as_view('username_exists_api')
email_exists_view = EmailExists.as_view('email_exists_api')

public_blueprint.add_url_rule(
    '/public/',
    view_func=hello_view,
    methods=['GET']
)
public_blueprint.add_url_rule(
    '/public/db_meta_data',
    view_func=db_meta_data_view,
    methods=['GET']
)
public_blueprint.add_url_rule(
    '/public/random_username',
    view_func=random_username_view,
    methods=['GET']
)
public_blueprint.add_url_rule(
    '/public/data',
    view_func=full_data_view,
    methods=['GET']
)
public_blueprint.add_url_rule(
    '/public/update',
    view_func=update_data_view,
    methods=['GET']
)
public_blueprint.add_url_rule(
    '/public/exists/username',
    view_func=username_exists_view,
    methods=['GET']
)
public_blueprint.add_url_rule(
    '/public/exists/email',
    view_func=email_exists_view,
    methods=['GET']
)
