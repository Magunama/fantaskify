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
            deadline_box.text = self.deadline.strftime("%Y-%m-%d %H:%M")
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
        )
        self.menu.bind(on_release=self.menu_release)
        self.menu.bind(on_dismiss=self.menu_dismiss)

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

    def menu_release(self, instance, instance_menu_item):
        if not hasattr(instance_menu_item, "icon"):
            return
        if instance_menu_item.icon == "delete-outline":
            # upon deletion confirmation, purge task
            if instance_menu_item.theme_text_color == "Custom":
                self.menu.dismiss()
                self.destroy()
            # make label and icon red for confirmation
            else:
                instance_menu_item.theme_text_color = "Custom"
                instance_menu_item.text_color = 1, 0, 0, 1
                instance_menu_item.text = "Confirm?"

    def menu_dismiss(self, instance):
        # operation cancelled, restore colors if theme changed
        menu_box = instance.menu.ids.box
        menu_items = menu_box.children
        for item in menu_items:
            if item.theme_text_color == "Custom":
                menu_box.clear_widgets()
                instance.create_menu_items()
                return
