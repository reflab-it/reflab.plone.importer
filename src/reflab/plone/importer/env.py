from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy, OmnipotentUser
from zope.component.hooks import setSite


def init_app(app, user_id='reflab_importer', user_name='Reflab Importer'):
    _policy = PermissiveSecurityPolicy()
    setSecurityPolicy(_policy)
    user = OmnipotentUser()
    user._id = user_id
    user._name = user_name
    newSecurityManager(None, user.__of__(app.acl_users))
    return app


def init_portal(portal):
    setSite(portal)
    return portal