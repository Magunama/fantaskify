from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty
from content.templates.buttons import NewTaskButton


class TodayBar(MDBoxLayout):
    def menu_click(self, app):
        side_menu = app.root.ids.side_menu
        side_menu.open()

    def other(self):
        pass


class TodayBox(MDBoxLayout):
    pass


class Today(MDScreen):
    pass
