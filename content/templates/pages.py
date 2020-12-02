from kivy.app import App
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen

from content.objects.category import Category
from content.templates.buttons import NewNoteTaskButton
from content.objects.note import Note
from content.objects.task import Task
from pony import orm
import datetime


class PageBar(MDBoxLayout):
    title = StringProperty()

    def menu_click(self, app):
        side_menu = app.root.ids.side_menu
        side_menu.open()

    def other(self):
        pass


class PageBox(MDBoxLayout):
    pass


class Notes(MDScreen):
    def update(self):
        """(Re)Loads all notes into the notes list"""
        notes_box = self.ids.container
        notes_list = notes_box.ids.list
        notes_list.clear_widgets()
        with orm.db_session:
            app = App.get_running_app()
            notes = app.db.Notes.select()
            for n in notes:
                new_note = Note(title=n.title, description=n.description, db_id=n.id)
                notes_list.add_widget(new_note)


class TodayBox(PageBox):
    pass


class Today(MDScreen):
    def update(self):
        """(Re)Loads all tasks with the deadline today into the today list"""
        today_box = self.ids.container
        today_list = today_box.ids.list
        today_list.clear_widgets()
        with orm.db_session:
            app = App.get_running_app()
            tasks = app.db.Tasks.select()
            for t in tasks:
                today = datetime.date.today()
                if t.deadline and t.deadline.date() == today:
                    new_task = Task(title=t.title, deadline=t.deadline, db_id=t.id)
                    today_list.add_widget(new_task)


class Tasks(MDScreen):
    def update(self):
        """(Re)Loads all tasks into the tasks list"""
        tasks_box = self.ids.container
        tasks_list = tasks_box.ids.list
        tasks_list.clear_widgets()
        with orm.db_session:
            app = App.get_running_app()
            tasks = app.db.Tasks.select()
            for t in tasks:
                new_task = Task(title=t.title, deadline=t.deadline, db_id=t.id)
                tasks_list.add_widget(new_task)
