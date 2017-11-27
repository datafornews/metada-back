import datetime
from flask_admin import helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView, fields
from flask_admin.form.fields import Select2Field
from flask_admin.contrib.sqla.filters import BooleanEqualFilter

from flask_security import Security, SQLAlchemyUserDatastore, current_user
from wtforms.fields import PasswordField
from sqlalchemy_utils import Choice

from flask import url_for, redirect, request, abort
from flask import has_app_context


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


class RoleSafeModelView(SafeModelView):
    @property
    def column_list(self):
        if has_app_context() and current_user.has_role('superuser'):
            return self.superuser_column_list
        return self.moderator_column_list

    @property
    def _list_columns(self):
        return self.get_list_columns()

    @_list_columns.setter
    def _list_columns(self, value):
        pass

    @property
    def form_columns(self):
        if has_app_context() and current_user.has_role('superuser'):
            return self.superuser_form_columns
        return self.moderator_form_columns

    @property
    def _create_form_class(self):
        return self.get_create_form()

    @_create_form_class.setter
    def _create_form_class(self, value):
        pass

    @property
    def _edit_form_class(self):
        return self.get_edit_form()

    @_edit_form_class.setter
    def _edit_form_class(self, value):
        pass


class EntityModelView(RoleSafeModelView):
    ownership = [
        ('c', 'company'),
        ('i', 'individual'),
        ('m', 'media'),
        ('o', 'other')
    ]
    # column_searchable_list = ['name', 'wiki.title', 'id']
    column_searchable_list = ['name', 'id']

    superuser_column_list = ['name', 'website', 'wiki_link', 'long_name',
                             'other_groups', 'category',
                             'updated_by', 'updated_at', 'created_by', 'created_at', 'id' # 'wiki',
                             ]
    moderator_column_list = ['name', 'website', 'wiki_link', 'long_name',
                             'other_groups', 'category', 'id']
    superuser_form_columns = superuser_column_list[:-1]
    moderator_form_columns = moderator_column_list[:-1]

    column_sortable_list = ['name', 'id']
    column_editable_list = ['name', 'website', 'wiki_link',
                            'other_groups', 'long_name']

    form_overrides = dict(category=SelectForChoiceTypeField)
    form_args = {
        'category': {
            'choices': ownership,
        },
    }

    def on_model_change(self, form, entity, is_created):
        now = datetime.datetime.now()
        if is_created:
            entity.created_by = current_user
            entity.created_at = now
        entity.updated_by = current_user
        entity.updated_at = now


class WikiDataModelView(SafeModelView):
    column_searchable_list = ['title', 'lang', 'entity.name']
    column_list = ['title', 'lang', 'entity.name']
    column_editable_list = ['title', 'lang']

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False


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

    def on_model_change(self, form, user, is_created):
        if form.password2.data is not None:
            if form.password2.data != "":
                user.set_password(form.password2.data)

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False


class EdgeModelView(RoleSafeModelView):
    column_searchable_list = ['child.name', 'parent.name', 'value']

    superuser_column_list = ['parent', 'child', 'value', 'special',
                             'updated_by', 'updated_at', 'created_by', 'created_at']
    superuser_form_columns = superuser_column_list

    moderator_column_list = ['parent', 'child', 'value', 'special',]
    moderator_form_columns = moderator_column_list

    def on_model_change(self, form, edge, is_created):
        now = datetime.datetime.now()
        if is_created:
            edge.created_by = current_user
            edge.created_at = now
        edge.updated_by = current_user
        edge.updated_at = now


class DBMetadataModelView(SafeModelView):
    column_searchable_list = ['description', 'version', 'version_string']

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False
