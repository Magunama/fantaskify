from kivy.app import App

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.picker import MDDatePicker, MDTimePicker
from kivymd.uix.bottomsheet import MDCustomBottomSheet

from content.objects.task import Task
from content.objects.note import Note
from content.objects.category import Category

import datetime


class NewNoteDialogScreen(MDFloatLayout):
    def __init__(self, bottom_sheet):
        super().__init__()
        self.bottom_sheet = bottom_sheet

    def text_field_validate(self, text_field):
        pass

    def confirm_button_release(self):
        title_field = self.ids.title_field
        desc_field = self.ids.desc_field

        app = App.get_running_app()
        notes = app.root.home.ids.notes
        notes_box = notes.ids.container
        notes_list = notes_box.ids.list

        title_text = title_field.text
        if not title_text:
            return
        desc_text = desc_field.text
        item = Note(title=title_text, description=desc_text)
        notes_list.add_widget(item)

        # close dialog (bottom sheet)
        self.bottom_sheet.dismiss()

        # save in db
        item.insert_into_db()


class NewTaskDialogScreen(MDFloatLayout):
    def __init__(self, bottom_sheet):
        super().__init__()
        self.bottom_sheet = bottom_sheet
        self.deadline = [None, None]  # date, time

    def text_field_validate(self, text_field):
        pass

    def get_date(self, date):
        self.deadline[0] = date
        self.ids.date_button.text = str(date)
        self.ids.date_button.icon = "calendar-check"

        # show reset button
        self.ids.date_button.size_hint_x = 0.25
        self.ids.reset_date_button.opacity = 1
        self.ids.reset_date_button.disabled = False

    def show_date_picker(self):
        min_date = datetime.date.today()
        date_dialog = MDDatePicker(callback=self.get_date, min_date=min_date)
        date_dialog.open()

    def reset_date_picker(self):
        self.deadline[0] = None
        date_button = self.ids.date_button
        date_button.size_hint_x = 0.3
        date_button.text = "Date"
        date_button.icon = "calendar-blank"
        reset_date_button = self.ids.reset_date_button
        reset_date_button.opacity = 0
        reset_date_button.disabled = True

    def get_time(self, instance, time):
        self.deadline[1] = time
        self.ids.time_button.text = time.strftime("%H:%M")
        self.ids.time_button.icon = "clock-check-outline"

        # show reset button
        self.ids.time_button.size_hint_x = 0.15
        self.ids.reset_time_button.opacity = 1
        self.ids.reset_time_button.disabled = False

    def show_time_picker(self):
        previous_time = datetime.datetime.now()
        time_dialog = MDTimePicker()
        time_dialog.set_time(previous_time)
        time_dialog.bind(time=self.get_time)
        time_dialog.open()

    def reset_time_picker(self):
        self.deadline[1] = None
        time_button = self.ids.time_button
        time_button.size_hint_x = 0.2
        time_button.text = "Time"
        time_button.icon = "progress-clock"
        reset_time_button = self.ids.reset_time_button
        reset_time_button.opacity = 0
        reset_time_button.disabled = True

    def confirm_button_release(self):
        app = App.get_running_app()
        tasks = app.root.home.ids.tasks
        tasks_list = tasks.container.no_category_list

        title_field = self.ids.title_field
        title_text = title_field.text
        if not title_text:
            return

        date, time = self.deadline
        deadline = None
        if date:
            if not time:
                time = datetime.time()
            deadline = datetime.datetime.combine(date=date, time=time)
        else:
            if time:
                date = datetime.date.today()
                deadline = datetime.datetime.combine(date=date, time=time)

        if deadline and deadline <= datetime.datetime.now():
            return

        priority_slider = self.ids.priority_slider
        priority = int(priority_slider.value)

        item = Task(title=title_text, deadline=deadline, priority=priority)
        tasks_list.add_widget(item)

        # close dialog (bottom sheet)
        self.bottom_sheet.dismiss()

        # save in db
        item.insert_into_db()


class NewNoteTaskDialog(MDCustomBottomSheet):
    def __init__(self, instance_icon):
        if instance_icon == "note":
            self.screen = NewNoteDialogScreen(self)
        else:
            self.screen = NewTaskDialogScreen(self)
        super().__init__(screen=self.screen)


class NewCategoryDialogScreen(MDBoxLayout):
    def __init__(self, bottom_sheet):
        super().__init__()
        self.bottom_sheet = bottom_sheet

    def confirm_button_release(self):
        title_field = self.title_field

        app = App.get_running_app()
        tasks = app.root.home.ids.tasks
        category_box = tasks.container.category_box

        title_text = title_field.text
        if not title_text:
            # todo: send error message
            return

        item = Category(title=title_text)
        category_box.add_widget(item)

        # close dialog (bottom sheet)
        self.bottom_sheet.dismiss()

        # save in db
        item.insert_into_db()


class NewCategoryDialog(MDCustomBottomSheet):
    def __init__(self):
        self.screen = NewCategoryDialogScreen(self)
        super().__init__(screen=self.screen)
