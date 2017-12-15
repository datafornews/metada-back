from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
import datetime
import uuid
from flask_security.utils import verify_password

from app import bcrypt, db
from app.models.User_model import User, BlacklistToken, VerifiedEmail
import app.forms.Validation as Val
from app.utils.mail import send_register_email
from app.utils.jwt import get_jwt_user
from app.utils.models_to_dict import user_to_dict
from flask_cors import CORS

auth_blueprint = Blueprint('auth', __name__)
CORS(auth_blueprint, resources=r'/auth/*')

fail_responses = {
    'username_exists': {
        'status': 'fail',
        'message': 'usernameExists',
    },
    'email_exists': {
        'status': 'fail',
        'message': 'emailExists',
    },
    'invalid_form': {
        'status': 'fail',
        'message': 'invalidForm',
    },
    'error': {
        'status': 'fail',
        'message': 'error'
    }

}


class RegisterAPI(MethodView):
    """
    User Registration Resource
    """

    def post(self):
        # get the post data
        responseObject = fail_responses['error']
        post_data = Val.register_user(request.get_json())
        if post_data:
            # check if user already exists
            user_mail = User.query.filter_by(
                email=post_data.get('email')).first()
            user_username = User.query.filter_by(
                username=post_data.get('username')).first()

            if not user_mail:
                if not user_username:
                    try:
                        user = User(username=post_data.get('username'),
                                    first_name=post_data.get('firstName'),
                                    last_name=post_data.get('lastName'),
                                    email=post_data.get('email'),
                                    password=post_data.get('password'),
                                    active=True)
                        user.registered_on = datetime.datetime.utcnow()
                        vf = VerifiedEmail()
                        vf.created_at = user.registered_on
                        vf.user = user
                        vf.link = str(uuid.uuid4())

                        email_response = send_register_email(user)

                        db.session.add(user)
                        db.session.commit()
                        # generate the auth token
                        auth_token = user.encode_auth_token(user.id)
                        responseObject = {
                            'status': 'success',
                            'message': 'registered',
                            'auth_token': auth_token.decode(),
                            'user': user_to_dict(user)
                        }
                        print('User {} added'.format(user.username))
                        return make_response(jsonify(responseObject)), 201
                    except Exception as e:
                        print('ERROR', e)
                        responseObject = fail_responses['error']
                else: 
                    responseObject = fail_responses['username_exists']
            else:
                responseObject = fail_responses['email_exists']
        else:
            responseObject = fail_responses['invalid_form']

        return make_response(jsonify(responseObject)), 401


class ResendEmailAPI(MethodView):

    def post(self):
        post_data = request.get_json()
        result = get_jwt_user(request)
        if not result['allow']:
            return make_response(jsonify(result['response'])), 401

        user = result['response']
        if not user:
            return make_response(
                jsonify({'status': 'fail', 'message': 'noUser'})), 401

        now = datetime.datetime.utcnow()
        if now - user.verified_email.created_at > datetime.timedelta(
                hours=1):
            email_response = send_register_email(user)
            user.verified_email.created_at = now
            db.object_session(user).commit()
            print('email resent')
            return make_response(jsonify({'resent': True})), 200
        else:
            print('email not sent')
            return make_response(jsonify({'resent': False})), 200


class LoginAPI(MethodView):
    """
    User Login Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        try:
            # fetch the user data
            user = User.query.filter_by(
                email=post_data.get('email')
            ).first()
            if user and verify_password(
                    post_data.get('password'), user.password):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode(),
                        'user': user_to_dict(user)
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'invalidUser'
                }
                return make_response(jsonify(responseObject)), 404
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject)), 500


class UserAPI(MethodView):
    """
    User Resource
    """

    def post(self):
        result = get_jwt_user(request)
        print(result)
        if not result['allow']:
            return make_response(jsonify(result['response'])), 401

        user = result['response']
        if not user:
            return make_response(
                jsonify({'status': 'fail', 'message': 'noUser'})), 401
        else:
            auth_header = request.headers.get('Authorization')
            auth_token = auth_header.split(" ")[1]
            blacklist_token = BlacklistToken(token=auth_token)
            db.session.add(blacklist_token)
            db.session.commit()
            auth_token = user.encode_auth_token(user.id)
            return make_response(
                jsonify({
                    'status': 'success',
                    'userData': user_to_dict(user),
                    'auth_token': auth_token.decode()
                })), 200


class LogoutAPI(MethodView):
    """
    Logout Resource
    """

    def post(self):
        # get auth token
        result = get_jwt_user(request)
        if not result['allow']:
            return make_response(jsonify(result['response'])), 401

        user = result['response']
        if not user:
            return make_response(
                jsonify({'status': 'fail', 'message': 'noUser'})), 401

        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1]

        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            # mark the token as blacklisted
            blacklist_token = BlacklistToken(token=auth_token)
            try:
                # insert the token
                db.session.add(blacklist_token)
                db.session.commit()
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged out.'
                }
                print(user, '-> Logged Out')
                return make_response(jsonify(responseObject)), 200
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': e
                }
                return make_response(jsonify(responseObject)), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401

        return make_response(jsonify(responseObject)), 403


# define the API resources
registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')
user_view = UserAPI.as_view('user_api')
logout_view = LogoutAPI.as_view('logout_api')
resend_view = ResendEmailAPI.as_view('resend_email_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/status',
    view_func=user_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/logout',
    view_func=logout_view,
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/resend_email',
    view_func=resend_view,
    methods=['POST']
)
