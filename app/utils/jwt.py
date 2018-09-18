from flask import request, make_response, jsonify
from app.models.User_model import User
<<<<<<< HEAD
from app import db
import datetime
from app.utils.responses import jwt_fail_responses
import uuid

=======
import datetime
>>>>>>> 992afbcd411a29a14ac37b0585f9a511767535b7


def get_user(request):
    return get_jwt_user(request, should_be_confirmed=False)


def get_confimed_user(request):
    return get_jwt_user(request, should_be_confirmed=True)


def get_jwt_user(request, should_be_confirmed=False):
    """Check jwt and return user

    Checks that the requet's jwt is in the header and valid.
    If should_be_confirmed is True, then the user should be confirmed.

    If not it does not allow access it returns a response with status 
    "fail" and message:
        - noAuthHeader: no Authorization header found in the request
        - malformed: Authorization header is not of the form "Bearer jwt"
        - blacklisted: Token is blacklisted and can't be used anymore
        - invalid: Token has been altered
        - expired: Token has expired
        - userNotConfirmed: Token is valid but associated user is not confirmed

    If access is allowed, status is "success" and the message contains
    the user model object


    Arguments:
        request -- Only exists within the context of a request
        should_be_confirmed -> bool -- user should be confirmed?

    Returns:
        dict -- keys:
                    success -> string -- success or fail
                    response -> string -- not allow else user
    """

    # get the auth token
<<<<<<< HEAD
=======
    response = {
        'status': 'fail',
    }

>>>>>>> 992afbcd411a29a14ac37b0585f9a511767535b7
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
<<<<<<< HEAD
            #token header is malformed
            response = jwt_fail_responses['malformed']
            return response
    else:
        #request should have an Authorization header
        response = jwt_fail_responses['noAuthHeader']
        return response

    decoded_response = User.decode_auth_token(auth_token)
    print(decoded_response)

    if not decoded_response['message']:
        # for some reason the message is empty -> for instance 
        # the user has no uuid
        response = jwt_fail_responses['noDecodedResponseUUID']
        return response
    
    if decoded_response['status'] == "success":
        user = User.query.filter_by(
            uuid=decoded_response['message']).first()

        if not should_be_confirmed:
            response = {
                'status': 'success',
                'message': user
            }
        else:
            if isinstance(user.confirmed_at, datetime.datetime):
                response = {
                    'status': 'success',
                    'message': user
                }
            else:
                response = jwt_fail_responses['userNotConfirmed']
=======
            response['message'] = 'malformed'
            return response
    else:
        response['message'] = 'noAuthHeader'
        return response
    
    print(auth_token)
    decoded_response = User.decode_auth_token(auth_token)
    if decoded_response['status'] == "success":
        user = User.query.filter_by(
            uuid=decoded_response['message']).first()
        if not should_be_confirmed:
            response['status'] = 'success'
            response['message'] = user
        else:
            if isinstance(user.confirmed_at, datetime.datetime):
                response['status'] = 'success'
                response['message'] = user
            else:
                response['status'] = 'fail'
                response['message'] = 'userNotConfirmed'
>>>>>>> 992afbcd411a29a14ac37b0585f9a511767535b7
    else:
        response = decoded_response

    return response
