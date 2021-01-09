from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.list import IRightBodyTouch
from kivymd.uix.menu import MDDropdownMenu

from pony import orm as pony
import datetime


class Container(IRightBodyTouch, MDBoxLayout):
    pass


class Task(OneLineAvatarIconListItem):
    def __init__(self, **kw):
        super().__init__()
        self.title = kw.get("title")

        self.deadline = kw.get("deadline")
        deadline_box = self.deadline_box
        if self.deadline:
            self.height = dp(100)
            self._txt_bot_pad = dp(42)
            deadline_box.text = self.deadline.strftime("%Y-%m-%d %H:%M")
            deadline_box.icon = "calendar"

            # make radio icon red if task is overdue
            now = datetime.datetime.now()
            if now > self.deadline:
                self.radio_icon.text_color = 1, 0, 0, 1
                self.radio_icon.theme_text_color = "Custom"

        else:
            deadline_box.size_hint_y = None
            deadline_box.height = "0dp"
            deadline_box.icon = ""
        self.priority = kw.get("priority")
        self.db_id = kw.get("db_id")

        # fit buttons
        self.ids._right_container.width = self.right_container.width
        self.ids._right_container.x = self.right_container.width

        # 3dots menu
        menu_items = [
            {
                "text": "Open"
            },
            {
                "icon": "delete-outline",
                "text": f"Delete task"
            }
        ]
        self.menu = MDDropdownMenu(
            caller=self.menu_button,
            items=menu_items,
            width_mult=4,
        )
        self.menu.bind(on_release=self.menu_release)
        self.menu.bind(on_dismiss=self.menu_dismiss)

    title = StringProperty()

    @pony.db_session
    def insert_into_db(self):
        app = App.get_running_app()
        t = app.db.Tasks(title=self.title, deadline=self.deadline, priority=self.priority)
        # obtain new db id
        app.db.commit()
        self.db_id = t.id

    @pony.db_session
    def remove_from_db(self):
        app = App.get_running_app()
        app.db.Tasks[self.db_id].delete()

    def destroy(self):
        # todo: check naming
        app = App.get_running_app()
        notes_page = app.root.home.ids.notes
        notes_box = notes_page.ids.container
        notes_list = notes_box.ids.list
        notes_list.remove_widget(self)

        # remove from db
        self.remove_from_db()

        # update screen
        home_sm = app.root.home.screen_manager
        home_sm.current_screen.update()

    def complete(self):
        # todo: record completion
        self.destroy()

    def menu_release(self, instance, instance_menu_item):
        if not hasattr(instance_menu_item, "icon"):
            return
        if instance_menu_item.icon == "delete-outline":
            # upon deletion confirmation, purge task
            if instance_menu_item.theme_text_color == "Custom":
                self.menu.dismiss()
                self.destroy()
            # make label and icon red for confirmation
            else:
                instance_menu_item.theme_text_color = "Custom"
                instance_menu_item.text_color = 1, 0, 0, 1
                instance_menu_item.text = "Confirm?"

    def menu_dismiss(self, instance):
        # operation cancelled, restore colors if theme changed
        menu_box = instance.menu.ids.box
        menu_items = menu_box.children
        for item in menu_items:
            if item.theme_text_color == "Custom":
                menu_box.clear_widgets()
                instance.create_menu_items()
                return

    def move_task(self, position):
        app = App.get_running_app()
        current_screen = app.root.home.screen_manager.current_screen
        no_category_list = current_screen.container.no_category_list
        category_box = current_screen.container.category_box

        # create a dict representing the tasks on the screen
        tasks = {0: []}
        for t in no_category_list.children:
            tasks[0].insert(0, t.db_id)
        for c in category_box.children:
            if c.db_id not in tasks:
                tasks[c.db_id] = list()
            for t in c.content.children:
                tasks[c.db_id].insert(0, t.db_id)

        # locate the current task
        curr_id = self.db_id
        with pony.db_session:
            curr_cat_id = app.db.Tasks[curr_id].category_id
            if curr_cat_id is None:
                curr_cat_id = 0
        curr_idx = tasks[curr_cat_id].index(curr_id)

        # decide where to move the current task
        target_idx = curr_idx + 1
        if position == "up":
            target_idx = curr_idx - 1
        if 0 <= target_idx < len(tasks[curr_cat_id]):
            if tasks[curr_cat_id][curr_idx] == tasks[curr_cat_id][target_idx]:
                return

            # stay in the same category, but swap places
            target_id = tasks[curr_cat_id][target_idx]
            from content.templates.pages import Tasks
            Tasks.db_swap(curr_id, target_id)
            current_screen.update(leave_open=curr_cat_id)

        else:
            # todo: ask if category should be changed?

            # change category and swap with the first/last (if necessary)
            category_ids = list(tasks)
            category_ids.sort()
            curr_cat_idx = category_ids.index(curr_cat_id)
            target_cat_idx = (curr_cat_idx + 1) % len(category_ids)
            if position == "up":
                target_cat_idx = (curr_cat_idx - 1) % len(category_ids)
            target_cat_id = category_ids[target_cat_idx]
            if target_cat_id == curr_cat_id:
                return

            with pony.db_session:
                curr_data = app.db.Tasks[curr_id]
                curr_data.category_id = target_cat_id
            current_screen.update(leave_open=target_cat_id if target_cat_id != 0 else None)
