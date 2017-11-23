import os
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, url_for, redirect, request, abort

from flask_security import Security, SQLAlchemyUserDatastore

from flask_bcrypt import Bcrypt

from flask_admin import Admin, form
from flask_admin import helpers as admin_helpers



app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)
CORS(app)
db = SQLAlchemy(app)

from app.models import Graph_model, User_model
from app.admin import model_views

from app import views

user_datastore = SQLAlchemyUserDatastore(db, User_model.User, User_model.Role)
security = Security(app, user_datastore)


admin = Admin(
    app,
    'OOP',
    base_template='master_security.html',
    template_mode='bootstrap3',
)

admin.add_view(model_views.EntityModelView(Graph_model.Entity, db.session))
admin.add_view(model_views.WikiDataModelView(Graph_model.WikiData, db.session))
admin.add_view(model_views.EdgeModelView(Graph_model.Edge, db.session))
admin.add_view(model_views.DBMetadataModelView(
    Graph_model.DBMetaData, db.session))
admin.add_view(model_views.UserModelView(User_model.User, db.session))


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
