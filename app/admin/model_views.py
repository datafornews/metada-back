from flask_admin import helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView, fields
from flask_admin.form.fields import Select2Field

from flask_security import Security, SQLAlchemyUserDatastore, current_user
from wtforms.fields import PasswordField
from sqlalchemy_utils import Choice

from flask import url_for, redirect, request, abort


class SelectField(Select2Field):
    def process_data(self, value):
        if value is None:
            self.data = None
        else:
            try:
                if isinstance(value, Choice):
                    self.data = self.coerce(value.code)
                else:
                    self.data = self.coerce(value)
            except (ValueError, TypeError):
                self.data = None


class SelectForChoiceTypeField(SelectField):
    def process_data(self, value):
        if value is None:
            self.data = None
        else:
            try:
                if isinstance(value, Choice):
                    self.data = self.coerce(value.code)
                else:
                    self.data = self.coerce(value)
            except (ValueError, TypeError):
                self.data = None


class SafeModelView(ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('moderator'):
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
    ownership = [
        ('c', 'company'),
        ('i', 'individual'),
        ('m', 'media'),
        ('o', 'other')
    ]
    # column_searchable_list = ['name', 'wiki.title', 'id']
    column_searchable_list = ['name', 'id']

    # column_list = ['name', 'website', 'wiki_link', 'wiki', 'long_name',
    #                'other_groups',
    #                'category', 'parents', 'children', 'id']
    column_list = ['name', 'website', 'wiki_link', 'long_name',
                   'other_groups', 'category', 'id']
    column_sortable_list = ['name', 'id']

    column_editable_list = ['name', 'website', 'wiki_link',
                            'other_groups', 'long_name']

    form_columns = ['name', 'category', 'website',
                    'wiki_link', 'long_name', 'other_groups']
    form_overrides = dict(category=SelectForChoiceTypeField)

    form_args = {
        'category': {
            'choices': ownership,
        },
    }
            


class WikiDataModelView(SafeModelView):
    column_searchable_list = ['title', 'lang', 'entity.name']
    column_list = ['title', 'lang', 'entity.name']
    column_editable_list = ['title', 'lang']


class UserModelView(SafeModelView):
    # https://stackoverflow.com/questions/39185230/flask-admin-overrides-password-when-user-model-is-changed
    column_searchable_list = ['email', 'first_name', 'last_name']

    column_list = ['first_name', 'last_name', 'email', 'roles',
                   'active', 'confirmed_at', 'registered_on', 'password']

    form_excluded_columns = ('password')
    #  Form will now use all the other fields in the model

    #  Add our own password form field - call it password2
    form_extra_fields = {
        'password2': PasswordField('Change Password to')
    }

    # set the form fields to use
    form_columns = ('email',
                    'password2',
                    'first_name',
                    'last_name',
                    'active',
                    'confirmed_at',
                    'registered_on',
                    'roles',
                    )

    def on_model_change(self, form, User, is_created):
        if form.password2.data is not None:
            if form.password2.data != "":
                User.set_password(form.password2.data)

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False


class EdgeModelView(SafeModelView):
    column_searchable_list = ['child.name', 'parent.name', 'value']


class DBMetadataModelView(SafeModelView):
    column_searchable_list = ['description', 'version', 'version_string']

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False
