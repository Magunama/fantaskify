from kivy.app import App
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
from pony.orm import db_session


class Note(MDCard):
    def __init__(self, **kw):
        title = kw.get("title")
        description = kw.get("description")
        super().__init__(title=title, description=description)
        self.db_id = kw.get("db_id")

    title = StringProperty()
    description = StringProperty()

    @db_session
    def insert_into_db(self):
        app = App.get_running_app()
        n = app.db.Notes(title=self.title, description=self.description)
        # obtain new db id
        app.db.commit()
        self.db_id = n.id

    @db_session
    def remove_from_db(self):
        app = App.get_running_app()
        app.db.Notes[self.db_id].delete()

    def destroy(self):
        app = App.get_running_app()
        notes_page = app.root.ids.notes
        notes_box = notes_page.ids.container
        notes_list = notes_box.ids.list
        notes_list.remove_widget(self)

        # remove from db
        self.remove_from_db()

    def delete(self):
        if self.delete_button.theme_text_color == "Custom":
            self.destroy()
        else:
            self.delete_button.theme_text_color = "Custom"
            self.delete_button.text_color = 1, 0, 0, 1
