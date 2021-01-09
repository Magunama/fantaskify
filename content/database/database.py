import datetime
from pony import orm

from kivy.utils import platform


db = orm.Database()


class Notes(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str)
    date_added = orm.Required(datetime.datetime, default=datetime.datetime.now())
    description = orm.Optional(str)


class Tasks(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str)
    priority = orm.Required(int, default=0)
    date_added = orm.Required(datetime.datetime, default=datetime.datetime.now())
    deadline = orm.Optional(datetime.datetime)
    category_id = orm.Optional(int)
    label = orm.Optional(str)

    @property
    def is_today(self):
        return self.deadline.date() == datetime.date.today()

    def in_category(self, category_id):
        return self.category_id == category_id


class Categories(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str)
    date_added = orm.Required(datetime.datetime, default=datetime.datetime.now())


class Settings(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    theme = orm.Optional(str)
    style = orm.Optional(str)


def load():
    global db
    db_path = ""
    if platform == "android":
        from android.storage import app_storage_path
        db_path = str(app_storage_path())
    db_path = db_path + "database.sqlite"
    db.bind(provider="sqlite", filename=db_path, create_db=True)
    try:
        db.generate_mapping()
        db.create_tables()
    except Exception as e:
        print(e)
        # corrupted database, attempting to recreate
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
    return db
