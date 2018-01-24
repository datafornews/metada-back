fail_list = ['email_exists',
             'invalid_email',
             'invalid_form',
             'invalid_username',
             'no_user',
             'no_user_for_email',
             'request_too_recent',
             'server_error',
             'username_exists',
             'wrong_password',
             ]

jwt_fail_list = [
    "noAuthHeader",
    "malformed",
    "blacklisted",
    "invalid",
    "expired",
    "userNotConfirmed",
]


def camel_case(s):
    s = ''.join(c.capitalize() for c in s.split('_'))
    return s[:1].lower() + s[1:]


fail_responses = {
    k: {
        'status': 'fail',
        'message': camel_case(k)
    } for k in fail_list
}

jwt_fail_responses = {
    k: {
        'status': 'fail',
        'message': camel_case(k)
    } for k in jwt_fail_list
}