import app.models

models_dict = vars(app.models)
models = dict([(name.lower(), cls) for name, cls in models_dict.items() if isinstance(cls, type)])

"""
When Django is presented with multiple databases, it relies on a database router to handle which database to 
perform operations on. 
This router class takes any models with a Database class with a defined db value and directs them towards that database
instead. If no value is provided, the default database will be used. 
"""


class DBRouter(object):
    @staticmethod
    def db_for_read(model, **hints):
        # Read from the correct database
        if not model or not hasattr(model, 'Database'):
            return None

        return getattr(model.Database, 'db', None)

    @staticmethod
    def db_for_write(model, **hints):
        # Write to the correct database
        if not model or not hasattr(model, 'Database'):
            return None

        return getattr(model.Database, 'db', None)

    @staticmethod
    def allow_migrate(db, app_label, model_name=None, **hints):
        if model_name is None:
            return False

        model = models.get(model_name.lower())

        if not model or not hasattr(model, 'Database'):
            return False

        # Retrieve the `db` attribute from the model's Database class
        meta_db = getattr(model.Database, 'db', None)

        # Allow migration only if the `db` matches
        return meta_db == db
