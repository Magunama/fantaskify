from kivy.app import App
from kivymd.uix.button import MDFloatingActionButtonSpeedDial
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from content.templates.dialogs import NewBottomDialog


class NewNoteTaskButton(MDFloatingActionButtonSpeedDial):
    count = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = {
            "note": "Note",
            "briefcase-clock": "Task",
        }

    def callback(self, instance):
        NewBottomDialog(instance.icon).open()
