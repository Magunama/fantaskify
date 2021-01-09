from kivy.properties import StringProperty
from kivy.app import App

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from pony.orm import db_session


class CategoryContent(MDBoxLayout):
    """Custom content."""


class Category(MDExpansionPanel):
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        super().__init__(
            panel_cls=MDExpansionPanelOneLine(text=self.title),
            content=CategoryContent()
        )

        self.db_id = kwargs.get("db_id")

    title = StringProperty()

    @db_session
    def insert_into_db(self):
        app = App.get_running_app()
        c = app.db.Categories(title=self.title)
        # obtain new db id
        app.db.commit()
        self.db_id = c.id
