from kivymd.uix.button import MDFloatingActionButton


class NewTaskButton(MDFloatingActionButton):
    def on_release(self):
        print("I will add something!")
