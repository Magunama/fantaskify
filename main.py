from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from content.templates.pages import Notes, Today
from content.side_menu import SideMenu
from content.database import database


class Home(MDScreen):
    pass


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = database.db

    def build(self):
        Window.softinput_mode = "pan"
        # Window.size = 1080, 2160
        # Window.size = 540, 1080
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.theme_style = "Dark"
        return Home()

    def on_start(self):
        screen_manager = self.root.ids.screen_manager
        screen_manager.current_screen.update()
        # self.fps_monitor_start()
        print("Started!")

    def on_stop(self):
        print("Stopped!")


MainApp().run()
