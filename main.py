import flet as ft
import pystray
import PIL.Image
import PIL
import random
import assets.backend as backend
import threading
import time
import sys as system
import os

class system_calls:
    def __init__(self,image_path,Page:ft.Page):
        self.image_path = PIL.Image.open(self.resource_path(image_path))
        self.page = Page
        self.running = False
        self.min_tray = pystray.Icon(name="To-do (flet app)",icon=self.image_path,menu=pystray.Menu(
            pystray.MenuItem("Open",self.show_window),
            pystray.MenuItem("Exit",self.exit_window)
        ))
    
    def hide_window(self):
        self.running = True
        self.page.window.always_on_bottom = False
        self.page.window.minimized = True
        self.page.window.maximizable = False
        self.page.update()

    def show_window(self):
        self.running = False
        self.page.window.skip_task_bar = False
        self.page.window.maximizable = False
        self.page.window.minimized = False
        self.page.window.skip_task_bar = True
        self.page.window.always_on_bottom = True
        self.min_tray.stop()
        self.page.update()

    def exit_window(self):
        self.min_tray.stop()
        self.page.window.destroy()
    
    def ini_tray(self):
        return pystray.Icon(name="To-do (flet app)",icon=self.image_path,menu=pystray.Menu(
            pystray.MenuItem("Open",self.show_window),
            pystray.MenuItem("Exit",self.exit_window)
        ))
    
    def resource_path(self,relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller onefile """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = system._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

class theme_colors:
    def __init__(self):
        self.background = "#121212"
        self.surface = "#444444"
        self.primary = "#BB86FC"
        self.secondary = "#16e91b"
        self.on_background = "#8f8f8f"
        self.on_surface = "#FFFFFF"
        self.on_primary = "#000000"
        self.on_secondary = "#000000"

class Task(ft.Column):

    def __init__(self,taskname,task_changed,taskdelete):
        super().__init__()
        self.colors = theme_colors()
        self.data_base = backend.DataClass()
        self.taskname = taskname
        self.task_changed = task_changed
        self.taskdelete = taskdelete
        self.completed = False
        self.paused = False
        self.timerDone = True
        self.timer = 0
        self.timePassed = 0
        self.timerThread = None
        self.event_thread = threading.Event()
        self.timeButton = ft.IconButton(
                    icon=ft.icons.PUNCH_CLOCK_OUTLINED,
                    tooltip="Add time to the task",
                    icon_color=self.colors.primary,
                    on_click= lambda _: self.page.open(self.timepick)
                )
        self.progress = ft.ProgressBar(
            value=0,
            width=400,
            color=self.colors.primary,
            bgcolor=self.colors.surface,
            visible=False,
        )
        self.startButton = ft.IconButton(
                        icon=ft.icons.PLAY_ARROW_OUTLINED,
                        visible=False,
                        tooltip="Edit the task",
                        icon_color=self.colors.primary,
                        on_click=self.handle_start_pause,)
        self.display_task = ft.Checkbox(label=self.check_name(),value=False,on_change=self.task_changes)
        self.timepick = ft.TimePicker(confirm_text="Set",
            error_invalid_text="Time out of range",
            help_text="Set timer",
            time_picker_entry_mode= ft.TimePickerEntryMode.INPUT_ONLY,
            on_change=self.handle_change,)
        
        self.edit_name = ft.TextField(expand=1,
                                      hint_style=ft.TextStyle(color=self.colors.on_background),
                                      border_color=self.colors.primary,
                                      color=self.colors.on_surface,
                                      on_focus=self.on_edit_field_click)

        self.display_view = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.display_task,
                    ft.Row(
                        spacing=0,
                        controls=[
                        self.startButton,
                        ft.IconButton(
                        icon=ft.icons.CREATE_OUTLINED,
                        icon_color=self.colors.primary,
                        tooltip="Edit the task",
                        on_click=self.edit_task,),
                        ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE_OUTLINED,
                        icon_color=self.colors.primary,
                        tooltip="Delete the task",
                        on_click=self.delete_task,),
                        ],
                    ),
                ],
            )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                self.timeButton,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    tooltip="Save the edited task",
                    icon_color=self.colors.surface,
                    on_click= self.save_edit,
                ),
            ],
        )

        self.controls = [self.display_view,self.edit_view,self.progress]
    
    def check_name(self):
        if len(self.taskname) > 31 :
            newtask,garValue = self.taskname.split(self.taskname[29:])
            self.tooltip = self.taskname
            return newtask+"..."

    def handle_change(self,e):
        hr,min,sec= str(self.timepick.value).split(":")
        hr = int(hr)
        min = int(min)
        sec = int(sec)
        self.timer = self.data_base.set_timer_task(hr,min,sec)
        self.timePassed = self.timer
        self.paused = True
        self.timerDone = False
        self.startButton.visible = True
        self.display_task.disabled = True
        self.progress.visible = True
        t1 = threading.Thread(target=self.timer_clock,args=())
        self.timerThread = t1
        self.task_changed()

    def handle_start_pause(self,e):
        self.paused = not self.paused
        if not self.paused:
            self.startButton.icon = ft.icons.PAUSE_CIRCLE_OUTLINE_OUTLINED
            self.timerThread.start()

        else:
            self.startButton.icon = ft.icons.PLAY_ARROW_OUTLINED
            self.event_thread.set()
            t1 = threading.Thread(target=self.timer_clock,args=())
            self.timerThread = t1  
        self.update()

    def timer_clock(self):
        print("timer started")
        seconds = self.timer
        while seconds > 0:
            if not self.event_thread.is_set():
                seconds -= 1
                self.progress.value = (self.timePassed - seconds)/self.timePassed
                self.timer = seconds
                self.update() 
                time.sleep(1)
            else:
                print("timer paused")
                self.event_thread.clear()
                return
        self.timerDone = True
        self.display_task.disabled = False
        self.startButton.icon = ft.icons.PLAY_ARROW_OUTLINED
        self.startButton.disabled = True
        self.timer = 0
        self.timePassed = 0
        self.paused = False
        self.task_changed()

    def handle_entry_mode_change(self,e):
        pass

    def edit_task(self,e):
        self.edit_name.hint_text = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()
        self.edit_name.value = self.display_task.label

    def task_changes(self,e):
        self.completed = self.display_task.value
        self.task_changed()

    def on_edit_field_click(self,e):
        self.edit_name.value = self.display_task.label
        self.update()

    def save_edit(self,e):
        self.display_task.label = self.edit_name.value
        self.edit_view.visible = False
        self.display_view.visible = True
        self.edit_name.value = ""
        self.update()

    def delete_task(self,e):
        self.taskdelete(self)

class Todo(ft.Column):

    def __init__(self,page):
        super().__init__()
        self.colors = theme_colors()
        self.data_base = backend.DataClass()
        self.taskfield = ft.TextField(hint_text=self.rand_hint_str(),
                             expand=True,
                             border_color=self.colors.primary,
                             color=self.colors.on_surface,
                             hint_style=ft.TextStyle(color=self.colors.on_background))
        self.floataddbutton = ft.FloatingActionButton(icon=ft.icons.ADD,on_click=self.add_task,bgcolor=self.colors.primary)
        self.completedbutton = ft.TextButton(text="Delete Completed",
                                             style=ft.ButtonStyle(color=self.colors.on_background,
                                                                  side=ft.BorderSide(1,self.colors.primary)),
                                             on_click=self.remove_completed_task)
        self.task_view = ft.Column(scroll=ft.ScrollMode.ALWAYS,height=200,spacing=10)
        self.items_left = ft.Text("0 item(s) left",color=self.colors.on_background)
        self.filter = ft.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="All"),ft.Tab(text="Active"),ft.Tab(text="Complete")],
            divider_color=self.colors.background,
            label_color= self.colors.primary,
            indicator_color=self.colors.primary,
        )
        self.width = 600
        self.controls = [
                         ft.Row(controls=[
                             self.taskfield,
                             self.floataddbutton
                         ]),
                         ft.Column(
                             spacing=25,
                             controls=[
                                 self.filter,
                                 self.task_view,
                                 ft.Row(
                                     alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                     vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                     controls=[
                                         self.items_left,
                                         self.completedbutton,
                                     ]
                                 )
                             ]
                         )
                     ]

    def before_update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        dicts = {}
        for task in self.task_view.controls:
            if not task.timerDone:
                task.display_task.disabled = True
            else:
                task.display_task.disabled = False
            
            if task.timer < task.timePassed:
                task.timeButton.disabled = True
                
            task.visible = (
                status == "All"
                or (status == "Active" and task.completed == False)
                or (status == "Complete" and task.completed == True)
            )
            
            dicts[task.taskname] = {"completed":task.completed,"timer":task.timePassed}
            if not task.completed:
                count = count + 1
        
        self.data_base.add_task(dicts)
        self.items_left.value = f"{count} item(s) left"

    def add_task(self,e):
        task = Task(self.taskfield.value,self.task_changed,self.task_delete)
        self.task_view.controls.append(task)
        self.taskfield.value = ""
        self.taskfield.hint_text = self.rand_hint_str()
        self.update()

    def task_delete(self,task):
        lists = []
        lists.append(task.taskname)
        self.task_view.controls.remove(task)
        self.data_base.remove_task(lists)
        self.update()

    def task_changed(self):
        self.update()

    def tabs_changed(self,e):
        self.update()
    
    def task_status_changed(self,e):
        self.update()

    def remove_completed_task(self,e):
        lists = []
        for task in self.task_view.controls:
            if task.completed == True:
                self.task_view.controls.remove(task)
                lists.append(task.taskname)
        self.update()
        self.data_base.remove_task(lists)

    def rand_hint_str(self):
        arr_choices = ["What's needs to be done? (˶ᵔ ᵕ ᵔ˶)","Got anything new to do ? ᐠ( ᐛ )ᐟ","Let's note the task you want to be done ( • ̀ω•́ )✧"]
        string = random.choice(arr_choices)
        return string
    def initialise_list(self):
        
        list_task = self.data_base.load_task()
        if list_task is not None:
            for item in list_task:
                task = Task(item,self.task_changed,self.task_delete)
                task.display_task.value = list_task[item]["completed"]
                task.completed = list_task[item]["completed"]
                task.timer = list_task[item]["timer"]
                if task.timer > 0:
                    task.timePassed = task.timer
                    task.paused = True
                    task.timerDone = False
                    task.startButton.visible = True
                    task.display_task.disabled = True
                    task.progress.visible = True
                    t1 = threading.Thread(target=task.timer_clock,args=())
                    task.timerThread = t1
                self.task_view.controls.append(task)
        

def main(page: ft.Page):
    app = Todo(page)
    sys = system_calls('assets/icon2.png',page)
    def minimise_window(e):
        if (e.data == 'close' or e.data == 'minimize') and sys.running == False:
            sys.hide_window()
            sys.min_tray = sys.ini_tray()
            sys.min_tray.run()
    page.add(app)
    page.title = "To-do"
    page.window.width = 400
    page.window.height = 500
    page.window.resizable = False
    page.bgcolor = app.colors.background
    page.theme = ft.Theme(scrollbar_theme=ft.ScrollbarTheme(thickness=3))
    app.initialise_list()
    page.window.skip_task_bar = True
    page.window.always_on_bottom = True
    page.window.prevent_close = True
    page.window.maximizable = False
    page.window.on_event = minimise_window
    page.update()

ft.app(main)