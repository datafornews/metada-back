import os
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, url_for, redirect, request, abort

from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_bcrypt import Bcrypt

from flask_admin import Admin, form
from flask_admin import helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView, fields


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)
CORS(app)
db = SQLAlchemy(app)

from app.models import Graph_model, User_model

from app import views

user_datastore = SQLAlchemyUserDatastore(db, User_model.User, User_model.Role)
security = Security(app, user_datastore)


class SafeModelView(ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

class EntityModelView(SafeModelView):
    column_searchable_list = ['name']
    column_list = ['name', 'website', 'wiki', 'wiki_page_id', 'category',
                   'long_name', 'other_groups', 'parents', 'children']
    column_editable_list = ['name', 'website', 'wiki', 'wiki_page_id','other_groups', 'long_name']

class UserModelView(SafeModelView):
    column_searchable_list = ['email', 'first_name', 'last_name']


class EdgeModelView(SafeModelView):
    column_searchable_list = ['child.name', 'parent.name']

class DBMetadataModelView(SafeModelView):
    column_searchable_list = ['description', 'version', 'version_string']


admin = Admin(
    app,
    'OOP',
    base_template='master_security.html',
    template_mode='bootstrap3',
)

admin.add_view(EntityModelView(Graph_model.Entity, db.session))
admin.add_view(EdgeModelView(Graph_model.Edge, db.session))
admin.add_view(DBMetadataModelView(Graph_model.DBMetaData, db.session))
admin.add_view(UserModelView(User_model.User, db.session))

@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

from app.auth.views import auth_blueprint
app.register_blueprint(auth_blueprint)