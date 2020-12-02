from kivy.app import App
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.list import IRightBodyTouch
from kivymd.uix.menu import MDDropdownMenu
from pony.orm import db_session
import datetime


class Container(IRightBodyTouch, MDBoxLayout):
    pass


class Task(MDCard):
    def __init__(self, **kw):
        super().__init__()
        self.title = kw.get("title")

        self.deadline = kw.get("deadline")
        deadline_box = self.deadline_box
        if self.deadline:
            deadline_box.label = self.deadline.strftime("%Y-%m-%d %H:%M")
            deadline_box.icon = "calendar"

            # make radio icon red if task is overdue
            now = datetime.datetime.now()
            if now > self.deadline:
                self.radio_icon.text_color = 1, 0, 0, 1
                self.radio_icon.theme_text_color = "Custom"

        else:
            deadline_box.size_hint_y = None
            deadline_box.height = "0dp"
            deadline_box.icon = ""
        self.db_id = kw.get("db_id")

        # fit buttons
        self.content.ids._right_container.width = self.right_container.width
        self.content.ids._right_container.x = self.right_container.width

        # 3dots menu
        menu_items = [
            {
                "text": "Open"
            },
            {
                "icon": "delete-outline",
                "text": f"Delete task"
            }
        ]
        self.menu = MDDropdownMenu(
            caller=self.menu_button,
            items=menu_items,
            width_mult=4,
            callback=self.menu_callback
        )

    title = StringProperty()

    @db_session
    def insert_into_db(self):
        app = App.get_running_app()
        t = app.db.Tasks(title=self.title, deadline=self.deadline)
        # obtain new db id
        app.db.commit()
        self.db_id = t.id

    @db_session
    def remove_from_db(self):
        app = App.get_running_app()
        app.db.Tasks[self.db_id].delete()

    def destroy(self):
        app = App.get_running_app()
        notes_page = app.root.ids.notes
        notes_box = notes_page.ids.container
        notes_list = notes_box.ids.list
        notes_list.remove_widget(self)

        # remove from db
        self.remove_from_db()

        # update screen
        screen_manager = app.root.ids.screen_manager
        screen_manager.current_screen.update()

    def complete(self):
        # todo: record completion
        self.destroy()

    def menu_callback(self, instance):
        if instance.icon == "delete-outline":
            if instance.theme_text_color == "Custom":
                self.menu.dismiss()
                self.destroy()
            else:
                instance.theme_text_color = "Custom"
                instance.text_color = 1, 0, 0, 1
                instance.text = "Confirm?"
