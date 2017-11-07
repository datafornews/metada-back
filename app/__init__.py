import os
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, url_for, redirect, request, abort

from flask_security import Security, SQLAlchemyUserDatastore, login_required, current_user

from flask_admin import Admin, form
from flask_admin import helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView, fields


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db = SQLAlchemy(app)

from app import graph_models, user_models
from app import views

user_datastore = SQLAlchemyUserDatastore(db, user_models.User, user_models.Role)
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


class EdgeModelView(SafeModelView):
    column_searchable_list = ['child.name', 'parent.name']


admin = Admin(
    app,
    'OOP',
    base_template='master_security.html',
    template_mode='bootstrap3',
)

admin.add_view(EntityModelView(graph_models.Entity, db.session))
admin.add_view(EdgeModelView(graph_models.Edge, db.session))

@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )
