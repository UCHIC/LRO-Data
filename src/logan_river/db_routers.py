import sys


class LRORouter(object):
    def db_for_read(self, model, **hints):
        is_testing = 'test' in sys.argv
        if model._meta.app_label == 'odm' or is_testing:
            return 'odm'
        return 'default'

    def db_for_write(self, model, **hints):
        is_testing = 'test' in sys.argv
        if model._meta.app_label == 'odm' or is_testing:
            return 'odm'
        return 'default'

    def allow_migrate(self, db, app_label, **hints):
        is_testing = 'test' in sys.argv
        unmanaged_apps = ['odm', ]
        allow = app_label not in unmanaged_apps or is_testing
        return allow
