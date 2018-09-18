# from app import app, db, user_models, user_datastore
from app import app
from flask_security.utils import encrypt_password


def build_sample_db():
    """
    Populate a small db with some example entries.
    """
    if 'yes' not in input('CREATE SUPERUSER?  '):
        return

    import string
    import random

    db.create_all()

    with app.app_context():
        # user_role = user_models.Role(name='user')
        # moderator_role = user_models.Role(name='moderator')
        # super_user_role = user_models.Role(name='superuser')
        # db.session.add(user_role)
        # db.session.add(moderator_role)
        # db.session.add(super_user_role)
        # db.session.commit()

        user_role = [r for r in user_models.Role.query.all()if r.name=='user'][0]
        moderator_role = [r for r in user_models.Role.query.all()if r.name=='moderator'][0]
        super_user_role = [r for r in user_models.Role.query.all()if r.name=='superuser'][0]

        first_name = db.Column(db.String(255))
        last_name = db.Column(db.String(255))
        email = db.Column(db.String(255), unique=True)
        password = db.Column(db.String(255))

        test_user = user_datastore.create_user(
            first_name='Victor',
            last_name='Schmidt',
            email='vsch@protonmail.com',
            password=encrypt_password(XXXX),
            roles=[user_role, super_user_role, moderator_role]
        )
        db.session.commit()
    return


if __name__ == '__main__':
    # build_sample_db()
    app.run(debug=True)
