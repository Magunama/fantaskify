from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from content.templates.pages import Notes, Today
from content.side_menu import SideMenu
from content.database import database

from pony import orm


class Home(MDScreen):
    pass


class Main(MDScreen):
    pass


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = database.load()

    def build(self):
        Window.softinput_mode = "pan"
        # Window.size = 1080, 2160
        # Window.size = 540, 1080

        with orm.db_session:
            settings = self.db.Settings.select().first()
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.theme_style = "Dark"
        if settings:
            if settings.theme:
                self.theme_cls.primary_palette = settings.theme
            if settings.style:
                self.theme_cls.theme_style = settings.style

        return Main()

    def on_start(self):
        home_sm = self.root.home.screen_manager
        home_sm.toolbar.update(home_sm.current_screen.name)
        home_sm.current_screen.update()
        # self.fps_monitor_start()
        print("Started!")

    def on_stop(self):
        print("Stopped!")


MainApp().run()
