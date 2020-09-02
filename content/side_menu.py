from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty


class SideMenu(MDScreen):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

    def open(self):
        self.nav_drawer.set_state("open")
