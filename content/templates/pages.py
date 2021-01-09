from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import FadeTransition

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList
from kivymd.uix.menu import MDDropdownMenu, RightContent
from kivymd.uix.picker import MDThemePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.toolbar import MDToolbar
from kivymd.font_definitions import fonts

from content.templates.buttons import NewNoteTaskButton
from content.templates.dialogs import NewCategoryDialog
from content.objects.note import Note
from content.objects.task import Task
from content.objects.category import Category

from pony import orm


class RightPageMenuItemContent(RightContent):
    pass


class SearchTab(FloatLayout, MDTabsBase):
    title = StringProperty()
    search_bar_hint = StringProperty()

    def __init__(self, **kwargs):
        super(SearchTab, self).__init__(**kwargs)
        tab_icons = {
            "Notes": "\U000F039A",
            "Tasks": "\U000F10D0",
            "Categories": "\U000F0B9D"
        }
        self.text = f"[size=20][font={fonts[-1]['fn_regular']}]{tab_icons[self.title]}[/size][/font] {self.title}"

    def update_content(self):
        search_text = self.search_bar.text
        if not search_text:
            return

        ret = {
            "Notes": self.update_content_notes,
            "Tasks": self.update_content_tasks,
            "Categories": self.update_content_categories
        }
        ret[self.title](search_text)

    def nothing_found(self):
        label_list = MDList()
        label = MDLabel(text="Nothing found!")
        label_list.add_widget(label)
        self.results_box.add_widget(label_list)

    def update_content_notes(self, search_text):
        app = App.get_running_app()
        with orm.db_session:
            notes = app.db.Notes.select(lambda n: search_text.lower() in n.title.lower())
            self.results_box.clear_widgets()
            if len(notes) == 0:
                self.nothing_found()
                return
            notes_list = MDList()
            for n in notes:
                new_note = Note(title=n.title, description=n.description, db_id=n.id)
                notes_list.add_widget(new_note)
            self.results_box.add_widget(notes_list)

    def update_content_tasks(self, search_text):
        app = App.get_running_app()
        with orm.db_session:
            tasks = app.db.Tasks.select(lambda t: search_text in t.title)
            self.results_box.clear_widgets()
            if len(tasks) == 0:
                self.nothing_found()
                return
            tasks_list = MDList()
            for t in tasks:
                new_task = Task(title=t.title, deadline=t.deadline, db_id=t.id)
                tasks_list.add_widget(new_task)
            self.results_box.add_widget(tasks_list)

    def update_content_categories(self, search_text):
        app = App.get_running_app()
        with orm.db_session:
            categories = app.db.Categories.select(lambda c: search_text in c.title)
            self.results_box.clear_widgets()
            if len(categories) == 0:
                self.nothing_found()
                return
            for c in categories:
                panel = Category(title=c.title, db_id=c.id)
                category_list = panel.content
                tasks = app.db.Tasks.select(lambda t: t.category_id == c.id)
                for t in tasks:
                    new_task = Task(title=t.title, deadline=t.deadline, db_id=t.id)
                    category_list.add_widget(new_task)
                self.results_box.add_widget(panel)


class SearchScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tabs = self.ids.tabs
        tabs.add_widget(SearchTab(title="Notes"))
        tabs.add_widget(SearchTab(title="Tasks"))
        tabs.add_widget(SearchTab(title="Categories"))

    @staticmethod
    def back_to_home_screen():
        app = App.get_running_app()
        sm = app.root.screen_manager
        sm.transition = FadeTransition(duration=.2, clearcolor=app.theme_cls.bg_dark)
        sm.current = "Home"

    def on_tab_switch(*args):
        search_tab = args[2]
        search_tab.results_box.clear_widgets()
        search_bar = search_tab.search_bar
        search_bar.focus = True
        search_bar.text = ""
        search_bar.focus = False


class SettingsScreen(MDScreen):
    @staticmethod
    def back_to_home_screen():
        SearchScreen.back_to_home_screen()

    def show_theme_picker(self):
        theme_dialog = MDThemePicker()

        # todo: remove accent tab before drawing
        theme_tab = theme_dialog.children[0]
        theme_tab_bar = theme_tab.children[0]
        theme_tab_box = theme_tab_bar.children[0].children[0]
        accent_picker = theme_tab_box.children[1]
        theme_tab_box.remove_widget(accent_picker)
        theme_dialog.open()
        theme_dialog.bind(on_dismiss=self.save_theme)

    def save_theme(self, instance):
        app = App.get_running_app()
        theme = app.theme_cls.primary_palette
        style = app.theme_cls.theme_style
        with orm.db_session:
            settings = app.db.Settings.select().first()
            if settings:
                settings.theme = theme
                settings.style = style
            else:
                app.db.Settings(theme=theme, style=style)


class PageBar(MDToolbar):
    title = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 3dots menu
        self.menu = None
        self.submenu = None

    def update(self, title):
        self.title = title
        items = [
            {
                "icon": "refresh",
                "text": "Refresh",
            },
            {
                "icon": "sort",
                "text": "Sort by",
                "right_content_cls": RightPageMenuItemContent()
            }
        ]
        if not self.title == "Notes":
            items.append({
                "icon": "folder-plus-outline",
                "text": "Create new category"
            })
        self.menu = MDDropdownMenu(
            items=items,
            width_mult=5,
        )
        self.menu.bind(on_release=self.menu_release)
        self.submenu = None

    @staticmethod
    def side_menu_click(app):
        home_screen = app.root.home
        side_menu = home_screen.side_menu
        side_menu.open()

    @staticmethod
    def search():
        app = App.get_running_app()
        sm = app.root.screen_manager
        sm.transition = FadeTransition(duration=.2, clearcolor=app.theme_cls.bg_dark)
        if sm.has_screen("Search"):
            sm.current = "Search"
        else:
            sm.switch_to(SearchScreen(name="Search"))

    def page_menu_open(self):
        if not self.children:
            return
        right_action_items = self.children[0]
        page_menu_button = right_action_items.children[0]
        self.menu.caller = page_menu_button
        self.menu.open()

    def menu_release(self, menu, item):
        if item.icon == "refresh":
            app = App.get_running_app()
            home_sm = app.root.home.screen_manager
            home_sm.current_screen.update()
            menu.dismiss()
        elif item.icon == "folder-plus-outline":
            TasksPageBox.create_new_category()
            menu.dismiss()
        elif item.icon == "sort":
            if self.submenu:
                self.submenu.open()
                return
            submenu_items = [
                {
                    "icon": "sort-alphabetical-ascending",
                    "text": "Alphabetical order"
                },
                {
                    "icon": "sort-clock-ascending-outline",
                    "text": "Date added"
                }
            ]
            if not self.title == "Notes":
                submenu_items.extend([
                    {
                        "icon": "sort-calendar-ascending",
                        "text": "Deadline"
                    },
                    {
                        "icon": "sort-numeric-ascending",
                        "text": "Priority"
                    }
                ])
            self.submenu = MDDropdownMenu(
                caller=item,
                items=submenu_items,
                width_mult=4.2,
            )
            self.submenu.bind(on_dismiss=self.submenu_dismiss)
            self.submenu.bind(on_release=self.submenu_release)
            self.submenu.open()

    def submenu_dismiss(self, submenu):
        self.menu.dismiss()

    def submenu_release(self, submenu, item):
        self.submenu.dismiss()
        self.menu.dismiss()
        app = App.get_running_app()
        page = app.root.home.screen_manager.current_screen
        ret = {
            "Alphabetical order": page.sort_alphabetical,
            "Date added": page.sort_date,
        }
        if not page.name == "Notes":
            ret["Priority"] = page.sort_priority
            ret["Deadline"] = page.sort_deadline
        ret[item.text]()
        Snackbar(text=f"The content is now sorted by {item.text.lower()}!").open()


class NotesPageBox(MDBoxLayout):
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

    @staticmethod
    def cycle_permutation(perm):
        """
        from [[1, 2, 3, 4, 5], [3, 4, 5, 2, 1]]
        to   [[1,3], [2,4], [3,5], [4,2], [5,1]]
        """
        return [list(a) for a in zip(perm[0], perm[1]) if a[0] != a[1]]

    @staticmethod
    def db_swap(curr_id, target_id):
        app = App.get_running_app()
        with orm.db_session:
            curr_data = app.db.Notes[curr_id]
            curr_data_dict = curr_data.to_dict()
            del curr_data_dict["id"]

            target_data = app.db.Notes[target_id]
            target_data_dict = target_data.to_dict()
            del target_data_dict["id"]

            curr_data.set(**target_data_dict)
            target_data.set(**curr_data_dict)

    def sort(self, initial_note_ids, sorted_note_ids):
        cycle = self.cycle_permutation([initial_note_ids, sorted_note_ids])
        swapped = list()
        for pair in cycle:
            curr, target = pair
            if target not in swapped:
                self.db_swap(curr, target)
                swapped.append(curr)
        self.update()

    def sort_criteria(self, criteria):
        initial_note_ids = list()
        sorted_note_ids = list()
        with orm.db_session:
            app = App.get_running_app()
            notes = app.db.Notes.select()
            for n in notes:
                initial_note_ids.append(n.id)
            notes = notes.sort_by(criteria)
            for n in notes:
                sorted_note_ids.append(n.id)
        self.sort(initial_note_ids, sorted_note_ids)

    def sort_alphabetical(self):
        self.sort_criteria(lambda n: n.title)

    def sort_date(self):
        self.sort_criteria(lambda n: n.date_added)


class TasksPageBox(MDBoxLayout):
    @staticmethod
    def create_new_category():
        NewCategoryDialog().open()


class Today(MDScreen):
    def update(self, leave_open=None):
        """(Re)Loads all tasks with the deadline today into the today list"""
        app = App.get_running_app()

        # add tasks with no category
        no_category_list = self.container.no_category_list
        no_category_list.clear_widgets()
        with orm.db_session:
            tasks = app.db.Tasks.select(lambda t: t.is_today)
            for t in tasks:
                if t.category_id:
                    continue
                new_task = Task(title=t.title, deadline=t.deadline, db_id=t.id)
                no_category_list.add_widget(new_task)

        # add tasks in categories
        leave_open_panel = None
        category_box = self.container.category_box
        category_box.clear_widgets()
        with orm.db_session:
            categories = app.db.Categories.select()
            for c in categories:
                panel = Category(title=c.title, db_id=c.id)
                category_list = panel.content
                tasks = app.db.Tasks.select(lambda t: t.category_id == c.id and t.is_today)
                if len(tasks) == 0:
                    continue
                for t in tasks:
                    new_task = Task(title=t.title, deadline=t.deadline, db_id=t.id)
                    category_list.add_widget(new_task)
                category_box.add_widget(panel)

                if panel.db_id == leave_open:
                    leave_open_panel = panel
        if leave_open_panel:
            def check_open_panel(dt):
                leave_open_panel.check_open_panel(leave_open_panel)
            Clock.schedule_once(check_open_panel)

    def sort(self, initial_note_ids, sorted_note_ids, swap_type="t"):
        cycle = Notes.cycle_permutation([initial_note_ids, sorted_note_ids])
        swapped = list()
        for pair in cycle:
            curr, target = pair
            if target not in swapped:
                Tasks.db_swap(curr, target, swap_type)
                swapped.append(curr)
        self.update()

    def sort_criteria(self, t_criteria, c_criteria):
        app = App.get_running_app()

        # sort tasks with no cat first
        initial_task_ids = list()
        sorted_task_ids = list()
        with orm.db_session:
            tasks = app.db.Tasks.select(lambda t: t.is_today and not t.category_id)
            for t in tasks:
                initial_task_ids.append(t.id)
            tasks = tasks.sort_by(t_criteria)
            for t in tasks:
                sorted_task_ids.append(t.id)
        self.sort(initial_task_ids, sorted_task_ids)

        today_categories = list()

        # then sort tasks inside each category (slow as heck)
        with orm.db_session:
            categories = app.db.Categories.select()
            for c in categories:
                initial_task_ids = list()
                sorted_task_ids = list()
                tasks = app.db.Tasks.select(lambda t: t.is_today and t.in_category(c.id))
                if len(tasks) == 0:
                    continue
                for t in tasks:
                    initial_task_ids.append(t.id)
                tasks = tasks.sort_by(t_criteria)
                for t in tasks:
                    sorted_task_ids.append(t.id)
                self.sort(initial_task_ids, sorted_task_ids)
                today_categories.append(c.id)

        # # also sort categories
        initial_cat_ids = list()
        sorted_cat_ids = list()
        with orm.db_session:
            categories = app.db.Categories.select(lambda c: c.id in today_categories)
            for c in categories:
                initial_cat_ids.append(c.id)
            categories = categories.sort_by(c_criteria)
            for c in categories:
                sorted_cat_ids.append(c.id)
        self.sort(initial_cat_ids, sorted_cat_ids, "c")

    def sort_alphabetical(self):
        self.sort_criteria(lambda t: t.title, lambda c: c.title)

    def sort_date(self):
        self.sort_criteria(lambda t: t.date_added, lambda c: c.date_added)

    def sort_priority(self):
        self.sort_criteria(lambda t: t.priority, lambda c: c.title)

    def sort_deadline(self):
        self.sort_criteria(lambda t: t.deadline, lambda c: c.title)


class Tasks(MDScreen):
    def update(self, leave_open=None):
        """(Re)Loads all tasks into the tasks list"""
        app = App.get_running_app()

        # add tasks with no category
        no_category_list = self.container.no_category_list
        no_category_list.clear_widgets()
        with orm.db_session:
            tasks = app.db.Tasks.select()
            for t in tasks:
                if t.category_id:
                    continue
                new_task = Task(title=t.title, deadline=t.deadline, db_id=t.id)
                no_category_list.add_widget(new_task)

        # add tasks in categories
        leave_open_panel = None
        category_box = self.container.category_box
        category_box.clear_widgets()
        with orm.db_session:
            categories = app.db.Categories.select()
            for c in categories:
                panel = Category(title=c.title, db_id=c.id)
                category_list = panel.content
                tasks = app.db.Tasks.select(lambda t: t.in_category(c.id))
                for t in tasks:
                    new_task = Task(title=t.title, deadline=t.deadline, db_id=t.id)
                    category_list.add_widget(new_task)
                category_box.add_widget(panel)

                if panel.db_id == leave_open:
                    leave_open_panel = panel
        if leave_open_panel:
            def check_open_panel(dt):
                leave_open_panel.check_open_panel(leave_open_panel)
            Clock.schedule_once(check_open_panel)

    @staticmethod
    def db_swap(curr_id, target_id, swap_type="t"):
        app = App.get_running_app()
        with orm.db_session:
            if swap_type == "t":
                curr_data = app.db.Tasks[curr_id]
                target_data = app.db.Tasks[target_id]
            else:
                curr_data = app.db.Categories[curr_id]
                target_data = app.db.Categories[target_id]

            curr_data_dict = curr_data.to_dict()
            del curr_data_dict["id"]
            target_data_dict = target_data.to_dict()
            del target_data_dict["id"]

            curr_data.set(**target_data_dict)
            target_data.set(**curr_data_dict)

    def sort(self, initial_note_ids, sorted_note_ids, swap_type="t"):
        cycle = Notes.cycle_permutation([initial_note_ids, sorted_note_ids])
        swapped = list()
        for pair in cycle:
            curr, target = pair
            if target not in swapped:
                self.db_swap(curr, target, swap_type)
                swapped.append(curr)
        self.update()

    def sort_criteria(self, t_criteria, c_criteria):
        app = App.get_running_app()

        # sort tasks with no cat first
        initial_task_ids = list()
        sorted_task_ids = list()
        with orm.db_session:
            tasks = app.db.Tasks.select(lambda t: not t.category_id)
            for t in tasks:
                initial_task_ids.append(t.id)
            tasks = tasks.sort_by(t_criteria)
            for t in tasks:
                sorted_task_ids.append(t.id)
        self.sort(initial_task_ids, sorted_task_ids)

        # also sort categories
        initial_cat_ids = list()
        sorted_cat_ids = list()
        with orm.db_session:
            categories = app.db.Categories.select()
            for c in categories:
                initial_cat_ids.append(c.id)
            categories = categories.sort_by(c_criteria)
            for c in categories:
                sorted_cat_ids.append(c.id)
        self.sort(initial_cat_ids, sorted_cat_ids, "c")

        # then sort tasks inside each category (slow as heck)
        with orm.db_session:
            categories = app.db.Categories.select()
            for c in categories:
                initial_task_ids = list()
                sorted_task_ids = list()
                tasks = app.db.Tasks.select(lambda t: t.in_category(c.id))
                for t in tasks:
                    initial_task_ids.append(t.id)
                tasks = tasks.sort_by(t_criteria)
                for t in tasks:
                    sorted_task_ids.append(t.id)
                self.sort(initial_task_ids, sorted_task_ids)

    def sort_alphabetical(self):
        self.sort_criteria(lambda t: t.title, lambda c: c.title)

    def sort_date(self):
        self.sort_criteria(lambda t: t.date_added, lambda c: c.date_added)

    def sort_priority(self):
        self.sort_criteria(lambda t: t.priority, lambda c: c.title)

    def sort_deadline(self):
        self.sort_criteria(lambda t: t.deadline, lambda c: c.title)
