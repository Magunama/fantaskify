from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem
from content.today import Today, TodayBox
from content.side_menu import SideMenu


class Home(MDScreen):
    pass


class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.theme_style = "Dark"
        return Home()

    def on_start(self):
        # self.fps_monitor_start()
        today = self.root.ids.today
        today_box = today.ids.container
        today_list = today_box.ids.list
        for i in range(0, 20):
            item = OneLineListItem(text=f"Single-line item {i}")
            today_list.add_widget(item)
        pass


MainApp().run()
