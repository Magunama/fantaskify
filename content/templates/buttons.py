from kivymd.uix.button import MDFloatingActionButtonSpeedDial
from content.templates.dialogs import NewNoteTaskDialog


class NewNoteTaskButton(MDFloatingActionButtonSpeedDial):
    count = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = {
            "note": "Note",
            "briefcase-clock": "Task",
        }

    def callback(self, instance):
        NewNoteTaskDialog(instance.icon).open()
