import datetime
from pony import orm

from kivy.utils import platform
db_path = ""
if platform == "android":
    from android.storage import app_storage_path
    db_path = str(app_storage_path())


db = orm.Database()


class Notes(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str)
    description = orm.Optional(str)


class Tasks(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str)
    deadline = orm.Optional(datetime.datetime)
    priority = orm.Required(int, default=0)
    category = orm.Optional(int)
    label = orm.Optional(str)


class Category(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str)


db_path = db_path + "database.sqlite"
db.bind(provider="sqlite", filename=db_path, create_db=True)
try:
    db.generate_mapping(create_tables=True)
except Exception as e:
    print("Corrupted database?\n" + str(e))
