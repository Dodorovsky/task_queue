import json
from task_queue.task import Task, TaskStatus


def save_tasks(tasks, filepath):
    data = []
    for task in tasks:
        data.append({
            "id": task.id,
            "description": task.description,
            "status": task.status.value
        })

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)



def load_tasks(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

    tasks = []
    for item in data:
        task = Task.from_dict(item)   
        tasks.append(task)

    return tasks









