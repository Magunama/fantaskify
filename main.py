from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from content.today import Today
from content.side_menu import SideMenu


class Home(MDScreen):
    pass


class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.theme_style = "Dark"
        return Home()


MainApp().run()
