from kivy.app import App
from main import structure


class MainApp(App):
    def build(self):
        self.title = "Magu's App"
        return structure()


if __name__ == '__main__':
    app = MainApp()
    app.run()