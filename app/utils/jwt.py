from flask import request, make_response, jsonify
from app.models.User_model import User


def get_jwt_user(request):
    """Check jwt and return user

    Checks that the requet's jwt is in the header and valid.
    If not it does not allow access it returns a response with status 
    "fail" and message:
        - noAuthHeader: no Authorization header found in the request
        - malformed: Authorization header is not of the form "Bearer jwt"
        - blacklisted: Token is blacklisted and can't be used anymore
        - invalid: Token has been altered
        - expired: Token has expired
    If access is allowed, the response contains the user model object


    Arguments:
        request -- Only exists within the context of a request

    Returns:
        dict -- keys:
                    allow -> Boolean, valid jwt
                    response -> string if not allow else user
    """

    # get the auth token
    auth_header = request.headers.get('Authorization')
    result = {
        'allow': False,
    }
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            result['response'] = {
                'status': 'fail',
                'message': 'malformed'
            }
    else:
        auth_token = ''
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            result['allow'] = True
            result['response'] = User.query.filter_by(id=resp).first()
        else:
            result['response'] = {
                'status': 'fail',
                'message': resp
            }
    else:
        result['response'] = {
            'status': 'fail',
            'message': 'noAuthHeader'
        }

    return result
