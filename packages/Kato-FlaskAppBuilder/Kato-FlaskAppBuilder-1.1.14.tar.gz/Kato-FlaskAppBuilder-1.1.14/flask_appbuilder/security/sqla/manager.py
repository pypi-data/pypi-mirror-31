import logging
import uuid
from sqlalchemy import func
from sqlalchemy.engine.reflection import Inspector
from werkzeug.security import generate_password_hash
from .models import User, Permission, PermissionView, RegisterUser, ViewMenu, Role, Role_Metadata
from ..manager import BaseSecurityManager
from ...models.sqla.interface import SQLAInterface
from ...models.sqla import Base
from ... import const as c
import requests;
import urllib3;
urllib3.disable_warnings();
from ...base import config_urls
import ast;
import json;
from urllib3.contrib import pyopenssl
pyopenssl.inject_into_urllib3()

log = logging.getLogger(__name__)


class SecurityManager(BaseSecurityManager):
    """
        Responsible for authentication, registering security views,
        role and permission auto management

        If you want to change anything just inherit and override, then
        pass your own security manager to AppBuilder.
    """
    user_model = User
    """ Override to set your own User Model """
    role_model = Role
    """ Override to set your own Role Model """
    permission_model = Permission
    viewmenu_model = ViewMenu
    permissionview_model = PermissionView
    registeruser_model = RegisterUser

    role_model_name = Role_Metadata


    def __init__(self, appbuilder):
        """
            SecurityManager contructor
            param appbuilder:
                F.A.B AppBuilder main object
        """
        super(SecurityManager, self).__init__(appbuilder)
        user_datamodel = SQLAInterface(self.user_model)
        role_model = (self.role_model);
        user_model = self.user_model;
        if self.auth_type == c.AUTH_DB:
            self.userdbmodelview.datamodel = user_datamodel
        elif self.auth_type == c.AUTH_LDAP:
            self.userldapmodelview.datamodel = user_datamodel
        elif self.auth_type == c.AUTH_OID:
            self.useroidmodelview.datamodel = user_datamodel
        elif self.auth_type == c.AUTH_OAUTH:
            self.useroauthmodelview.datamodel = user_datamodel
        elif self.auth_type == c.AUTH_REMOTE_USER:
            self.userremoteusermodelview.datamodel = user_datamodel
            self.userremoteusermodelview.role_model = role_model
            self.userremoteusermodelview.user_model = user_model;

        self.userstatschartview.datamodel = user_datamodel
        if self.auth_user_registration:
            self.registerusermodelview.datamodel = SQLAInterface(self.registeruser_model)

        self.rolemodelview.datamodel = SQLAInterface(self.role_model)
        self.permissionmodelview.datamodel = SQLAInterface(self.permission_model)
        self.viewmenumodelview.datamodel = SQLAInterface(self.viewmenu_model)
        self.permissionviewmodelview.datamodel = SQLAInterface(self.permissionview_model)
        self.rolemodelview.role_metadata = self.role_model_name;
        self.rolemodelview.role_model = self.role_model;
        self.create_db()

    @property
    def get_session(self):
        return self.appbuilder.get_session

    def register_views(self):
        super(SecurityManager, self).register_views()

    def create_db(self):
        try:
            engine = self.get_session.get_bind(mapper=None, clause=None)
            inspector = Inspector.from_engine(engine)
            if 'ab_user' not in inspector.get_table_names():
                log.info(c.LOGMSG_INF_SEC_NO_DB)
                Base.metadata.create_all(engine)
                log.info(c.LOGMSG_INF_SEC_ADD_DB)
            super(SecurityManager, self).create_db()
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_CREATE_DB.format(str(e)))
            exit(1)

    def find_register_user(self, registration_hash):
        return self.get_session.query(self.registeruser_model).filter(
            self.registeruser_model.registration_hash == registration_hash).scalar()

    def add_register_user(self, username, first_name, last_name, email,
                         password='', hashed_password=''):
        """
            Add a registration request for the user.

            :rtype : RegisterUser
        """
        register_user = self.registeruser_model()
        register_user.username = username
        register_user.email = email
        register_user.first_name = first_name
        register_user.last_name = last_name
        if hashed_password:
            register_user.password = hashed_password
        else:
            register_user.password = generate_password_hash(password)
        register_user.registration_hash = str(uuid.uuid1())
        try:
            self.get_session.add(register_user)
            self.get_session.commit()
            return register_user
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_ADD_REGISTER_USER.format(str(e)))
            self.appbuilder.get_session.rollback()
            return None

    def del_register_user(self, register_user):
        """
            Deletes registration object from database

            :param register_user: RegisterUser object to delete
        """
        try:
            self.get_session.delete(register_user)
            self.get_session.commit()
            return True
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_DEL_REGISTER_USER.format(str(e)))
            self.get_session.rollback()
            return False

    def find_user(self, username=None, email=None, token=None):
        """
            Finds user by username or email
        """
        if token:
            url = config_urls['SCOPE_WORKER_URL']
            if(url is None):
                return None;
            data = {'access_token':token};
            response = requests.get(url, data , verify = False);
            response = json.dumps(response.json());
            response = (json.loads(response));

            if(response['status'] == 200):

                data = response['data'];
                data = data[0];
                user =  self.get_session.query(self.user_model).filter_by(email = data['email']).first();
                if(user is None):
                    user = User();
                    return self.add_token_based_user(data,user);
                else:
                    return user;
            else:
                return None;
        if username:
            return self.get_session.query(self.user_model).filter(func.lower(self.user_model.username) == func.lower(username)).first()
        elif email:
            return self.get_session.query(self.user_model).filter_by(email=email).first();

    def get_all_users(self):
        return self.get_session.query(self.user_model).all()

    def add_token_based_user(self,data,user):
        roles = self.get_all_roles();
        role = 'gamma';
        if any(data['user_type'].lower() == role.name.lower() for role in roles):
            role = data['user_type'];
        elif 'admin' in data['user_type'].lower():
            role = 'admin';

        user_id = None;

        if 'company_id' in data:
            user_id = data['company_id'];
            user.user_parent = 'admin' if data['user_type'] == 'company' else 'company'

        if 'user_id' in data:
            user_id = data['user_id'];
            user.user_parent = 'admin' if data['user_type'] == 'vendor' else 'vendor'

        if 'sub_user_id' in data:
            user_id = data['sub_user_id'];
            user.user_parent = 'admin' if data['user_type'] == 'sub_vendor' else 'sub_vendor'

        if 'admin_id' in data:
            user_id = data['admin_id'];

        if user.user_parent is None:
            user.user_parent = 'admin';

        user.user_id = 1 if user_id is None else user_id;
        user.username = data['email'];
        user.email = data['email'];
        user.active = True;
        user.user_type = data['user_type'];
        role_output = self.get_session.query(self.role_model).filter(
            func.lower(self.role_model.name) == func.lower(role)).first();

        user.roles.append(role_output);

        username_f = data['username'] if 'username' in data else data['name'];
        name = username_f.split(" ", 1);
        user.first_name = name[0];
        user.last_name = "Scopeworker" if len(name) <= 1 else name[1];

        self.get_session.add(user);
        self.get_session.commit();
        log.info(c.LOGMSG_INF_SEC_ADD_USER.format(user.username))
        return user;
        # Create New Role TODO: add Role
        # Create Permission  TODO: add Permisisions

    def add_user(self, username, first_name, last_name, email, role, password='', hashed_password='' ):
        """
            Generic function to create user
        """
        try:
            user = self.user_model()
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.active = True
            user.roles.append(role),
            user.user_id = 1;
            user.user_type = 'company';
            if hashed_password:
                user.password = hashed_password
            else:
                user.password = generate_password_hash(password)
            self.get_session.add(user)
            self.get_session.commit()
            log.info(c.LOGMSG_INF_SEC_ADD_USER.format(username))
            return user
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_ADD_USER.format(str(e)))
            return False

    def count_users(self):
        return self.get_session.query(func.count('*')).select_from(self.user_model).scalar()

    def update_user(self, user):
        try:
            self.get_session.merge(user)
            self.get_session.commit()
            log.info(c.LOGMSG_INF_SEC_UPD_USER.format(user))
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_UPD_USER.format(str(e)))
            self.get_session.rollback()
            return False

    def get_user_by_id(self, pk):
        return self.get_session.query(self.user_model).get(pk)

    """
    -----------------------
     PERMISSION MANAGEMENT
    -----------------------
    """
    def add_role(self, name):
        role = self.find_role(name)
        if role is None:
            try:
                role = self.role_model()
                role.name = name
                self.get_session.add(role)
                self.get_session.commit()
                log.info(c.LOGMSG_INF_SEC_ADD_ROLE.format(name))
                return role
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_ROLE.format(str(e)))
                self.get_session.rollback()
        return role

    def add_role_name(self, name):
        role_name = self.find_role_metadata(name);
        if role_name is None:
            try:
                role_name = self.role_model_name();
                role_name.name = name;
                self.get_session.add(role_name)
                self.get_session.commit()
                log.info(c.LOGMSG_INF_SEC_ADD_ROLE.format(name))
                return role_name;
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_ROLE.format(str(e)))
                self.get_session.rollback();
        return role_name


    def find_role(self, name):
        return self.get_session.query(self.role_model).filter_by(name=name).first()

    def find_role_metadata(self, name):
        return self.get_session.query(self.role_model_name).filter_by(name=name).first();

    def get_all_roles(self):
        return self.get_session.query(self.role_model).all()

    def get_public_permissions(self):
        role = self.get_session.query(self.role_model).filter_by(name=self.auth_role_public).first()
        return role.permissions

    def find_permission(self, name):
        """
            Finds and returns a Permission by name
        """
        return self.get_session.query(self.permission_model).filter_by(name=name).first()

    def add_permission(self, name):
        """
            Adds a permission to the backend, model permission

            :param name:
                name of the permission: 'can_add','can_edit' etc...
        """
        perm = self.find_permission(name)
        if perm is None:
            try:
                perm = self.permission_model()
                perm.name = name
                self.get_session.add(perm)
                self.get_session.commit()
                return perm
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_PERMISSION.format(str(e)))
                self.get_session.rollback()
        return perm

    def del_permission(self, name):
        """
            Deletes a permission from the backend, model permission

            :param name:
                name of the permission: 'can_add','can_edit' etc...
        """
        perm = self.find_permission(name)
        if perm:
            try:
                self.get_session.delete(perm)
                self.get_session.commit()
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_DEL_PERMISSION.format(str(e)))
                self.get_session.rollback()

    """
    ----------------------
     PRIMITIVES VIEW MENU
    ----------------------
    """
    def find_view_menu(self, name):
        """
            Finds and returns a ViewMenu by name
        """
        return self.get_session.query(self.viewmenu_model).filter_by(name=name).first()

    def get_all_view_menu(self):
        return self.get_session.query(self.viewmenu_model).all()

    def add_view_menu(self, name):
        """
            Adds a view or menu to the backend, model view_menu
            param name:
                name of the view menu to add
        """
        view_menu = self.find_view_menu(name)
        if view_menu is None:
            try:
                view_menu = self.viewmenu_model()
                view_menu.name = name
                self.get_session.add(view_menu)
                self.get_session.commit()
                return view_menu
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_VIEWMENU.format(str(e)))
                self.get_session.rollback()
        return view_menu

    def del_view_menu(self, name):
        """
            Deletes a ViewMenu from the backend

            :param name:
                name of the ViewMenu
        """
        obj = self.find_view_menu(name)
        if obj:
            try:
                self.get_session.delete(obj)
                self.get_session.commit()
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_DEL_PERMISSION.format(str(e)))
                self.get_session.rollback()

    """
    ----------------------
     PERMISSION VIEW MENU
    ----------------------
    """
    def find_permission_view_menu(self, permission_name, view_menu_name):
        """
            Finds and returns a PermissionView by names
        """
        permission = self.find_permission(permission_name)
        view_menu = self.find_view_menu(view_menu_name)
        return self.get_session.query(self.permissionview_model).filter_by(permission=permission, view_menu=view_menu).first()

    def find_permissions_view_menu(self, view_menu):
        """
            Finds all permissions from ViewMenu, returns list of PermissionView

            :param view_menu: ViewMenu object
            :return: list of PermissionView objects
        """
        return self.get_session.query(self.permissionview_model).filter_by(view_menu_id=view_menu.id).all()

    def add_permission_view_menu(self, permission_name, view_menu_name):
        """
            Adds a permission on a view or menu to the backend

            :param permission_name:
                name of the permission to add: 'can_add','can_edit' etc...
            :param view_menu_name:
                name of the view menu to add
        """
        vm = self.add_view_menu(view_menu_name)
        perm = self.add_permission(permission_name)
        pv = self.permissionview_model()
        pv.view_menu_id, pv.permission_id = vm.id, perm.id
        try:
            self.get_session.add(pv)
            self.get_session.commit()
            log.info(c.LOGMSG_INF_SEC_ADD_PERMVIEW.format(str(pv)))
            return pv
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_ADD_PERMVIEW.format(str(e)))
            self.get_session.rollback()

    def del_permission_view_menu(self, permission_name, view_menu_name):
        try:
            pv = self.find_permission_view_menu(permission_name, view_menu_name)
            # delete permission on view
            self.get_session.delete(pv)
            self.get_session.commit()
            # if no more permission on permission view, delete permission
            pv = self.get_session.query(self.permissionview_model).filter_by(permission=pv.permission).all()
            if not pv:
                self.del_permission(pv.permission.name)
            log.info(c.LOGMSG_INF_SEC_DEL_PERMVIEW.format(permission_name, view_menu_name))
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_DEL_PERMVIEW.format(str(e)))
            self.get_session.rollback()

    def exist_permission_on_views(self, lst, item):
        for i in lst:
            if i.permission and i.permission.name == item:
                return True
        return False

    def exist_permission_on_view(self, lst, permission, view_menu):
        for i in lst:
            if i.permission.name == permission and i.view_menu.name == view_menu:
                return True
        return False

    def add_permission_role(self, role, perm_view):
        """
            Add permission-ViewMenu object to Role

            :param role:
                The role object
            :param perm_view:
                The PermissionViewMenu object
        """
        if perm_view not in role.permissions:
            try:
                role.permissions.append(perm_view)
                self.get_session.merge(role)
                self.get_session.commit()
                log.info(c.LOGMSG_INF_SEC_ADD_PERMROLE.format(str(perm_view), role.name))
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_PERMROLE.format(str(e)))
                self.get_session.rollback()

    def del_permission_role(self, role, perm_view):
        """
            Remove permission-ViewMenu object to Role

            :param role:
                The role object
            :param perm_view:
                The PermissionViewMenu object
        """
        if perm_view in role.permissions:
            try:
                role.permissions.remove(perm_view)
                self.get_session.merge(role)
                self.get_session.commit()
                log.info(c.LOGMSG_INF_SEC_DEL_PERMROLE.format(str(perm_view), role.name))
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_DEL_PERMROLE.format(str(e)))
                self.get_session.rollback()
