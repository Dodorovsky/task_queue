import dearpygui.dearpygui as dpg
from queue_manager import QueueManager
from task import TaskPriority, TaskStatus

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
    refresh_task_list()
    
def delete_task_callback(sender, app_data, user_data):
    task_id = user_data
    qm.delete_task(task_id)
    qm.save(qm.filepath)
    refresh_task_list()
    
def mark_done_callback(sender, app_data, user_data):
    task_id = user_data
    qm.mark_task_done(task_id)
    refresh_task_list()
    
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

    # update arrows
    dpg.set_item_label("btn_id", header_label("ID"))
    dpg.set_item_label("btn_desc", header_label("Description"))
    dpg.set_item_label("btn_status", header_label("Status"))
    dpg.set_item_label("btn_priority", header_label("Priority"))

    refresh_task_list()


def header_label(col):
    direction = sort_directions[col]
    arrow = " ^" if direction == 1 else " v"
   
    return f"{col}{arrow}"


def refresh_task_list():
    children = dpg.get_item_children("task_table", 1)
    if children:
        for row in children:
            dpg.delete_item(row)
            
    for t in qm.get_all_tasks():
        with dpg.table_row(parent="task_table"):
            dpg.add_text(str(t.id))
            dpg.add_text(t.description)
            dpg.add_text(t.status.value)
            priority_text = dpg.add_text(t.priority.name)

            if t.priority.name == "HIGH":
                dpg.bind_item_theme(priority_text, "priority_high_theme")
            elif t.priority.name == "MEDIUM":
                dpg.bind_item_theme(priority_text, "priority_medium_theme")
            else:
                dpg.bind_item_theme(priority_text, "priority_low_theme")


            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Done",
                    callback=mark_done_callback,
                    user_data=t.id
                )
                dpg.add_button(
                    label="Delete",
                    callback=delete_task_callback,
                    user_data=t.id
                )

dpg.create_context()

with dpg.window(label="Task Queue UI", width=600, height=400):
    dpg.add_text("Add a new task")

    dpg.add_input_text(label="Title", tag="title_input")
    dpg.add_combo(["LOW", "MEDIUM", "HIGH"],
                  default_value="MEDIUM",
                  label="Priority",
                  tag="priority_combo")
    dpg.add_button(label="Add Task", callback=add_task_callback)

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


    with dpg.group(horizontal=True):
        dpg.add_spacer(width=2)   

        dpg.add_button(label=header_label("ID"), tag="btn_id", callback=lambda: sort_by("ID"), width=100)
        dpg.add_button(label=header_label("Description"), tag="btn_desc", callback=lambda: sort_by("Description"), width=100)
        dpg.add_button(label=header_label("Status"), tag="btn_status", callback=lambda: sort_by("Status"), width=80)
        dpg.add_button(label=header_label("Priority"), tag="btn_priority", callback=lambda: sort_by("Priority"), width=120)

        dpg.add_spacer(width=140)  
    
    with dpg.child_window(tag="task_list_container", width=570, height=200, border=True):
        with dpg.table(tag="task_table", header_row=False):
            dpg.add_table_column(label="ID")
            dpg.add_table_column(label="Description")
            dpg.add_table_column(label="Status")
            dpg.add_table_column(label="Priority")
            dpg.add_table_column(label="Actions", width_fixed=True, width=140)

dpg.create_viewport(title="Task Queue UI", width=600, height=400)
dpg.setup_dearpygui()
refresh_task_list()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

