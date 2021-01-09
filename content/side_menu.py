from kivy.app import App
from kivy.uix.screenmanager import FadeTransition
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty

from content.templates.pages import SettingsScreen


class SideMenu(MDScreen):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

    def open(self):
        self.nav_drawer.set_state("open")

    def close(self):
        self.nav_drawer.set_state("close")

    def switch_screen(self, new_page):
        self.close()

        # set screen change animation
        screen_names = self.screen_manager.screen_names
        current = self.screen_manager.current
        current_idx = screen_names.index(current)
        new_page_idx = screen_names.index(new_page)
        self.screen_manager.transition.direction = "left"
        if new_page_idx < current_idx:
            self.screen_manager.transition.direction = "right"

        self.screen_manager.current = new_page
        self.screen_manager.toolbar.update(new_page)
        self.screen_manager.current_screen.update()

    def settings(self):
        app = App.get_running_app()
        sm = app.root.screen_manager
        sm.transition = FadeTransition(duration=.2, clearcolor=app.theme_cls.bg_dark)
        if sm.has_screen("Settings"):
            sm.current = "Settings"
        else:
            sm.switch_to(SettingsScreen(name="Settings"))
