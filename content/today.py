from kivymd.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen


class TodayBar(BoxLayout):
    def menu_click(self, app):
        side_menu = app.root.ids.side_menu
        side_menu.open()

    def other(self):
        pass


class TodayBox(ScrollView):
    pass


class Today(MDScreen):
    pass
