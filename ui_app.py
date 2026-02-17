import dearpygui.dearpygui as dpg
import queue_manager
import sys, os
from queue_manager import QueueManager
from task import TaskPriority, TaskStatus


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

selected_task_id = None

TASKS_FILE = "tasks.json"
qm = QueueManager(TASKS_FILE)

sort_directions = {
    "ID": 1,
    "Description": 1,
    "Status": 1,
    "Priority": 1
}

def add_task_callback():
    description = dpg.get_value("title_input")
    priority_label = dpg.get_value("priority_combo")

    if not description:
        return

    priority = TaskPriority[priority_label]  

    qm.add_task(description, priority)
    qm.save(qm.filepath)
    refresh_main_tasks()
    
    
def delete_task_callback(sender, app_data, user_data):
    task_id = user_data
    task = qm.get_task(task_id)
    parent = task.parent_id if task else None

    qm.delete_task(task_id)
    qm.save(qm.filepath)

    if parent is None:
        refresh_main_tasks()
        refresh_subtasks()
    else:
        refresh_subtasks()


    
def mark_done_callback(sender, app_data, user_data):
    task_id = user_data
    task = qm.get_task(task_id)
    parent = task.parent_id if task else None

    qm.mark_task_done(task_id)

    if parent is None:
        refresh_main_tasks()
    else:
        refresh_subtasks()


def mark_undone_callback(sender, app_data, user_data):
    task_id = user_data
    parent = qm.get_task(task_id).parent_id

    qm.mark_task_undone(task_id)

    if parent is None:
        refresh_main_tasks()
    else:
        refresh_subtasks()

    
def select_task_callback(sender, app_data, user_data):
    global selected_task_id
    selected_task_id = user_data  # user_data = id of the main task
    refresh_subtasks()            # refresh the lower window

    
def sort_by(column):
    direction = sort_directions[column]
    sort_directions[column] *= -1

    reverse = (direction == -1)

    if column == "ID":
        qm._tasks.sort(key=lambda t: t.id, reverse=reverse)
    elif column == "Description":
        qm._tasks.sort(key=lambda t: t.description.lower(), reverse=reverse)
    elif column == "Status":
        qm._tasks.sort(key=lambda t: t.status.value, reverse=reverse)
    elif column == "Priority":
        qm._tasks.sort(key=lambda t: t.priority.value, reverse=reverse)


    dpg.set_item_label("btn_desc", header_label("Description"))
    dpg.set_item_label("btn_status", header_label("Status"))
    dpg.set_item_label("btn_priority", header_label("Priority"))

    refresh_main_tasks()

def header_label(col):
    direction = sort_directions[col]
    arrow = " ^" if direction == 1 else " v"
   
    return f"{col}{arrow}"

def priority_callback(sender, app_data, user_data):
    task_id, new_priority = user_data
    qm.update_task_priority(task_id, new_priority)
    refresh_main_tasks()
   

def refresh_main_tasks():
    # borrar SOLO filas (slot 1)
    rows = dpg.get_item_children("main_tasks_table", 1)
    if rows:
        for r in rows:
            dpg.delete_item(r)

    for t in qm._tasks:
        if t.parent_id is not None:
            continue  # solo tareas principales

        with dpg.table_row(parent="main_tasks_table"):

            # Description
            if t.status == TaskStatus.DONE:
                desc_item = dpg.add_text(t.description)
                dpg.configure_item(desc_item, color=(180, 199, 224))
            else:
                desc_item = dpg.add_text(t.description)
                dpg.configure_item(desc_item, color=(150, 200, 255))

            # Status
            status_color = (237, 132, 0) if t.status != TaskStatus.DONE else (120, 220, 120)
            status_item = dpg.add_text(t.status.value)
            dpg.configure_item(status_item, color=status_color)

            # Priority (clickable)
            priority_tag = f"priority_text_{t.id}"
            priority_text = dpg.add_text(t.priority.name.upper(), tag=priority_tag)

            if t.priority.name == "HIGH":
                dpg.bind_item_theme(priority_text, "priority_high_theme")
            elif t.priority.name == "MEDIUM":
                dpg.bind_item_theme(priority_text, "priority_medium_theme")
            else:
                dpg.bind_item_theme(priority_text, "priority_low_theme")

            if t.status == TaskStatus.DONE:
                if t.priority.name == "HIGH":
                    dpg.configure_item(priority_text, color=(153, 93, 86))
                elif t.priority.name == "MEDIUM":
                    dpg.configure_item(priority_text, color=(153, 149, 86))
                else:
                    dpg.configure_item(priority_text, color=(86, 153, 96))

            # Popup para cambiar prioridad
            with dpg.popup(priority_tag, mousebutton=dpg.mvMouseButton_Left):
                dpg.add_button(label="LOW",    callback=priority_callback, user_data=(t.id, "LOW"))
                dpg.add_button(label="MEDIUM", callback=priority_callback, user_data=(t.id, "MEDIUM"))
                dpg.add_button(label="HIGH",   callback=priority_callback, user_data=(t.id, "HIGH"))

            # Action buttons
            with dpg.group(horizontal=True):

                # SELECT — vuelve aquí
                btn_select = dpg.add_button(
                    label="Select",
                    callback=select_task_callback,
                    user_data=t.id
                )

                btn_done = dpg.add_button(
                    label="Done",
                    callback=mark_done_callback,
                    user_data=t.id
                )
                btn_delete = dpg.add_button(
                    label="Delete",
                    callback=delete_task_callback,
                    user_data=t.id
                )
                btn_undone = dpg.add_button(
                    label="Undone",
                    callback=mark_undone_callback,
                    user_data=t.id
                )

                dpg.bind_item_theme(btn_done, "green_button_theme")
                dpg.bind_item_theme(btn_delete, "red_button_theme")
                dpg.bind_item_theme(btn_undone, "orange_button_theme")


def refresh_subtasks():
    # borrar SOLO filas (slot 1)
    rows = dpg.get_item_children("subtasks_table", 1)
    if rows:
        for r in rows:
            dpg.delete_item(r)

    if selected_task_id is None:
        return

    for t in qm._tasks:
        if t.parent_id != selected_task_id:
            continue

        with dpg.table_row(parent="subtasks_table"):

            # --- Description ---
            if t.status == TaskStatus.DONE:
                desc_item = dpg.add_text(t.description)
                dpg.configure_item(desc_item, color=(180, 199, 224))
            else:
                desc_item = dpg.add_text(t.description)
                dpg.configure_item(desc_item, color=(150, 200, 255))

            # --- Status ---
            status_color = (237, 132, 0) if t.status != TaskStatus.DONE else (120, 220, 120)
            status_item = dpg.add_text(t.status.value)
            dpg.configure_item(status_item, color=status_color)

            # --- Priority (clickable) ---
            priority_tag = f"sub_priority_text_{t.id}"
            priority_text = dpg.add_text(t.priority.name.upper(), tag=priority_tag)

            if t.priority.name == "HIGH":
                dpg.bind_item_theme(priority_text, "priority_high_theme")
            elif t.priority.name == "MEDIUM":
                dpg.bind_item_theme(priority_text, "priority_medium_theme")
            else:
                dpg.bind_item_theme(priority_text, "priority_low_theme")

            # override color if DONE
            if t.status == TaskStatus.DONE:
                if t.priority.name == "HIGH":
                    dpg.configure_item(priority_text, color=(153, 93, 86))
                elif t.priority.name == "MEDIUM":
                    dpg.configure_item(priority_text, color=(153, 149, 86))
                else:
                    dpg.configure_item(priority_text, color=(86, 153, 96))

            # popup para cambiar prioridad
            with dpg.popup(priority_tag, mousebutton=dpg.mvMouseButton_Left):
                dpg.add_button(label="LOW",    callback=priority_callback, user_data=(t.id, "LOW"))
                dpg.add_button(label="MEDIUM", callback=priority_callback, user_data=(t.id, "MEDIUM"))
                dpg.add_button(label="HIGH",   callback=priority_callback, user_data=(t.id, "HIGH"))

            # --- Action buttons ---
            with dpg.group(horizontal=True):

                if t.status == TaskStatus.PENDING:
                    btn_done = dpg.add_button(
                        label="Done",
                        callback=mark_done_callback,
                        user_data=t.id
                    )
                else:
                    btn_done = dpg.add_button(
                        label="Undone",
                        callback=mark_undone_callback,
                        user_data=t.id
                    )

                btn_delete = dpg.add_button(
                    label="Delete",
                    callback=delete_task_callback,
                    user_data=t.id
                )

                dpg.bind_item_theme(btn_done, "green_button_theme")
                dpg.bind_item_theme(btn_delete, "red_button_theme")


dpg.create_context()

with dpg.window(tag="main_window", label="Task Queue UI", width=782, height=710):
    dpg.add_text("Add a new task")

    dpg.add_input_text(label="Title", tag="title_input")
    dpg.add_combo(["LOW", "MEDIUM", "HIGH"],
                  default_value="MEDIUM",
                  label="Priority",
                  tag="priority_combo")
    add_task_btn = dpg.add_button(label="Add Task", callback=add_task_callback)

    dpg.add_spacer(height=10)
    dpg.add_text("Task List")
    
    with dpg.theme(tag="priority_high_theme"):
        with dpg.theme_component(dpg.mvText):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 80, 80))  

    with dpg.theme(tag="priority_medium_theme"):
        with dpg.theme_component(dpg.mvText):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 200, 0))  

    with dpg.theme(tag="priority_low_theme"):
        with dpg.theme_component(dpg.mvText):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (80, 200, 120))  
            
    with dpg.theme(tag="green_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (45, 87, 47), category=dpg.mvThemeCat_Core)

    with dpg.theme(tag="red_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (105, 34, 13), category=dpg.mvThemeCat_Core)

    with dpg.theme(tag="orange_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (112, 69, 6), category=dpg.mvThemeCat_Core)

    with dpg.theme(tag="header_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (71, 49, 46), category=dpg.mvThemeCat_Core)
            
    dpg.bind_item_theme(add_task_btn, "header_button_theme")
    

    with dpg.group(horizontal=True):
        dpg.add_spacer(width=0)   
        btn_desc = dpg.add_button(label=header_label("Description"), tag="btn_desc", callback=lambda: sort_by("Description"), width=300)
        btn_status = dpg.add_button(label=header_label("Status"), tag="btn_status", callback=lambda: sort_by("Status"), width=100)
        btn_priority = dpg.add_button(label=header_label("Priority"), tag="btn_priority", callback=lambda: sort_by("Priority"), width=100)
        btn_apcionts = dpg.add_button(label="Actions", tag="btn_actions", width=200)

    
    with dpg.child_window(tag="main_tasks_container", width=750, height=225, border=True):
        with dpg.table(
            tag="main_tasks_table",
            header_row=False,
            resizable=False,
            policy=dpg.mvTable_SizingFixedFit
        ):
            dpg.add_table_column(label="Description", width_fixed=True, init_width_or_weight=300)
            dpg.add_table_column(label="Status",      width_fixed=True, init_width_or_weight=100)
            dpg.add_table_column(label="Priority",    width_fixed=True, init_width_or_weight=100)
            dpg.add_table_column(label="Actions",     width_fixed=True, init_width_or_weight=230)
        
        
    dpg.bind_item_theme(btn_desc, "header_button_theme")
    dpg.bind_item_theme(btn_status, "header_button_theme")
    dpg.bind_item_theme(btn_priority, "header_button_theme")
    dpg.bind_item_theme(btn_apcionts, "header_button_theme")

    with dpg.group(horizontal=True):
        dpg.add_spacer(width=25)
        dpg.add_spacer(width=0)
        dpg.add_text("Subtasks", color=(200, 200, 200))  # título simple
        
    with dpg.group(horizontal=True):
        dpg.add_spacer(width=25)
        btn_desc_sub = dpg.add_button(label=header_label("Description"), tag="btn_desc_sub", width=300)
        btn_status_sub = dpg.add_button(label=header_label("Status"), tag="btn_status_sub", width=100)
        btn_priority_sub = dpg.add_button(label=header_label("Priority"), tag="btn_priority_sub", width=100)
        btn_actions_sub = dpg.add_button(label="Actions", tag="btn_actions_sub", width=160)

    with dpg.group(horizontal=True):
        dpg.add_spacer(width=18)
        with dpg.child_window(tag="subtasks_container", width=700, height=225, border=True):
            
            with dpg.table(
                tag="subtasks_table",
                header_row=False,
                resizable=False,
                policy=dpg.mvTable_SizingFixedFit
            ):
                
                dpg.add_table_column(label="Description", width_fixed=True, init_width_or_weight=300)
                dpg.add_table_column(label="Status",      width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Priority",    width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Actions",     width_fixed=True, init_width_or_weight=230)

        dpg.bind_item_theme(btn_desc_sub, "header_button_theme")
        dpg.bind_item_theme(btn_status_sub, "header_button_theme")
        dpg.bind_item_theme(btn_priority_sub, "header_button_theme")
        dpg.bind_item_theme(btn_actions_sub, "header_button_theme")

dpg.create_viewport(title="Task Queue UI", width=782, height=710, min_width=600, max_width=783,
                    min_height=450, max_height=720)
icon_path = resource_path("logo.ico")
dpg.set_viewport_small_icon(icon_path)
dpg.set_viewport_large_icon(icon_path)
dpg.setup_dearpygui()
dpg.set_primary_window("main_window", True)

print("Ventana principal existe:", dpg.does_item_exist("main_window"))
print("Parent de main_tasks_container:", dpg.get_item_parent("main_tasks_container"))
print("Tareas en memoria:", len(qm._tasks))
for t in qm._tasks:
    print("  -", repr(t), type(t), getattr(t, "status", None), getattr(t, "priority", None))

refresh_main_tasks()

dpg.show_viewport()
dpg.start_dearpygui()

