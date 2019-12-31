from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.uix.popup import Popup, PopupException
from kivy.graphics import *


class PopupGrid(Widget):
    pass


class LoginHolder(Widget):
    @staticmethod
    def empty_check(instance):
        if instance.text:  # textInput not empty
            return False
        return True

    def spawn_popup(self, reason):
        content = PopupGrid()
        # content.set_desc(reason)
        bt = Button(text='Close me!')
        content.add_widget(bt)
        bt.pos = content.center
        popup = Popup(title="Alert!", content=content, auto_dismiss=False)
        bt.bind(on_press=popup.dismiss)
        popup.open()

    def text_integrity(self, instance):
        empty = self.empty_check(instance)
        if empty:
            return False
        return True

    def login_button(self, name_obj, pword_obj):
        if not self.text_integrity(name_obj):
            return self.spawn_popup("Username area not filled properly!")
        if not self.text_integrity(pword_obj):
            return self.spawn_popup("Password area not filled properly!")
        name = name_obj.text
        pword = pword_obj.text
        if name == "test" and pword == "test":
            self.spawn_popup("You are in!")


class Start(Widget):
    pass


def structure():
    return Start()
