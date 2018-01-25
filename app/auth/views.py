from flask import Blueprint, request, make_response, jsonify, abort
from flask.views import MethodView
import datetime
import uuid
from flask_security.utils import verify_password

from app import bcrypt, db
from app.models.User_model import User, BlacklistToken, VerifiedEmail
import app.forms.Validation as Val
from app.utils.mail import send_register_email
from app.utils.jwt import get_user
from app.utils.models_to_dict import user_to_dict
from flask_cors import CORS
from app.utils.responses import fail_responses

auth_blueprint = Blueprint('auth', __name__)
CORS(auth_blueprint, resources=r'/auth/*')


class RegisterAPI(MethodView):
    """
    User Registration Resource
    """

    def post(self):
        # get the post data
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
                        auth_token = user.encode_auth_token(user.uuid)
                        response_object = {
                            'status': 'success',
                            'message': 'registered',
                            'auth_token': auth_token.decode(),
                            'user': user_to_dict(user)
                        }
                        print('User {} added'.format(user.username))
                        return make_response(jsonify(response_object)), 201
                    except Exception as e:
                        print('server_error', e)
                        response_object = fail_responses['server_error']
                        make_response(jsonify(response_object)), 500
                        return
                else:
                    response_object = fail_responses['username_exists']
            else:
                response_object = fail_responses['email_exists']
        else:
            response_object = fail_responses['invalid_form']

        return make_response(jsonify(response_object)), 401


class ResendEmailAPI(MethodView):

    def post(self):
        post_data = request.get_json()
        jwt_response = get_user(request)
        if jwt_response['status'] != "success":
            return make_response(jsonify(jwt_response)), 401

        user = jwt_response['message']
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

            if not user:
                response_object = fail_responses['no_user_for_email']
                return make_response(jsonify(response_object)), 401

            if not verify_password(
                    post_data.get('password'), user.password):
                response_object = fail_responses['wrong_password']
                return make_response(jsonify(response_object)), 401

            if not user.uuid:
                user.uuid = uuid.uuid4().__str__()
                db.object_session(user).commit()

            auth_token = user.encode_auth_token(user.uuid)

            if not auth_token:
                response_object = fail_responses['server_error']
                return make_response(jsonify(response_object)), 500

            response_object = {
                'status': 'success',
                'message': 'Successfully logged in.',
                'auth_token': auth_token.decode(),
                'user': user_to_dict(user)
            }
            return make_response(jsonify(response_object)), 200

        except Exception as e:
            print(e)
            response_object = fail_responses['server_error']
            return make_response(jsonify(response_object)), 500


class UserStatusAPI(MethodView):
    """
    User Resource
    """

    def post(self):
        jwt_response = get_user(request)
        if jwt_response['status'] != "success":
            return make_response(jsonify(jwt_response)), 401

        user = jwt_response['message']
        if not user:
            return make_response(
                jsonify(fail_responses['no_user'])), 401
        else:
            auth_header = request.headers.get('Authorization')
            auth_token = auth_header.split(" ")[1]
            blacklist_token = BlacklistToken(token=auth_token)
            db.session.add(blacklist_token)
            db.session.commit()
            auth_token = user.encode_auth_token(user.uuid)
            return make_response(
                jsonify({
                    'status': 'success',
                    'userData': user_to_dict(user),
                    'auth_token': auth_token.decode()
                })), 200

        return make_response(
            jsonify(fail_responses['server_error'])), 500


class EditUserAPI(MethodView):
    """
    Edit User Resource
    """

    def post(self):
        jwt_response = get_user(request)
        if jwt_response['status'] != "success":
            return make_response(jsonify(jwt_response)), 401

        user = jwt_response['message']

        if not user:
            return make_response(
                jsonify(fail_responses['no_user'])), 401

        post_data = request.get_json()

        data = Val.edit_user(post_data)


        if not data:
            print('Invalid Edit')
            return make_response(
                jsonify(fail_responses['invalid_form'])), 401

        if not verify_password(
                data['oldPassword'], user.password):
            response_object = fail_responses['wrong_password']
            return make_response(jsonify(response_object)), 401

        if data['username']:
            candidate_user = User.query.filter_by(
                email=data.get('username')).first()
            if candidate_user and not candidate_user.id == user.id:
                return make_response(
                    jsonify(fail_responses['username_exists'])), 401
            user.username = data['username']

        if data['email']:
            candidate_user = User.query.filter_by(
                email=data.get('email')).first()
            if candidate_user and not candidate_user.id == user.id:
                return make_response(
                    jsonify(fail_responses['email_exists'])), 401
            user.email = data['email']

        if data['password']:
            user.set_password(data['password'])
        
        user.last_name = data['last_name']
        user.first_name = data['first_name']

        db.object_session(user).commit()

        return make_response(
                    jsonify({
                        'status': 'success',
                        'message': user_to_dict(user)
                    })), 200




class LogoutAPI(MethodView):
    """
    Logout Resource
    """

    def post(self):
        # get auth token
        jwt_response = get_user(request)
        if jwt_response['status'] != "success":
            return make_response(jsonify(jwt_response)), 401

        user = jwt_response['message']
        if not user:
            return make_response(
                jsonify(fail_responses['no_user'])), 401

        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1]

        resp = User.decode_auth_token(auth_token)
        if resp['status'] == 'success':
            # mark the token as blacklisted
            blacklist_token = BlacklistToken(token=auth_token)
            try:
                # insert the token
                db.session.add(blacklist_token)
                db.session.commit()
                response_object = {
                    'status': 'success',
                    'message': 'Successfully logged out.'
                }
                print(user, '-> Logged Out')
                return make_response(jsonify(response_object)), 200
            except Exception as e:
                response_object = fail_responses['server_error']
                return make_response(jsonify(response_object)), 500
        else:
            response_object = resp
            return make_response(jsonify(response_object)), 401

        return make_response(jsonify(response_object)), 403


class Verify(MethodView):

    def get(self):
        # /auth/verify?link=
        vf_validity = 2  # days
        link = request.args.get('link')
        vf = VerifiedEmail.query.filter(VerifiedEmail.link == link).first()
        now = datetime.datetime.utcnow()
        if vf:
            if now - vf.created_at < datetime.timedelta(days=vf_validity):
                vf.user.confirmed_at = now
                vf.user.active = True
                db.object_session(vf).delete(vf)
                db.object_session(vf).commit()
                return jsonify({
                    'verified': True
                })
            return make_response(jsonify({"error": "outdated link"})), 404
        return abort(404)


# define the API resources
registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')
user_status_view = UserStatusAPI.as_view('user_api')
logout_view = LogoutAPI.as_view('logout_api')
resend_view = ResendEmailAPI.as_view('resend_email_api')
verify_view = Verify.as_view('verify_api')
edit_view = EditUserAPI.as_view('edit_view_api')

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
    view_func=user_status_view,
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

auth_blueprint.add_url_rule(
    '/auth/verify',
    view_func=verify_view,
    methods=['GET']
)

auth_blueprint.add_url_rule(
    '/auth/edit',
    view_func=edit_view,
    methods=['POST']
)
