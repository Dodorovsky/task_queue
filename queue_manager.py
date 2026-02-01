from task_queue.task import TaskStatus
from task_queue.storage import save_tasks, load_tasks
from task_queue.task import Task, TaskPriority
import json
class QueueManager:
    def __init__(self):
        self._tasks = []

    def add_task(self, description, priority=TaskPriority.MEDIUM):
        task = Task(description, priority=priority)
        self._tasks.append(task)
        return task

    def get_all_tasks(self):
        return list(self._tasks)

    def get_next_task(self):
        pending = [t for t in self._tasks if t.status == TaskStatus.PENDING]

        if not pending:
            return None

        # Ordenar por prioridad (desc) y luego por orden de llegada
        pending.sort(key=lambda t: t.priority.value, reverse=True)

        return pending[0]

    def mark_task_completed(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                task.status = TaskStatus.COMPLETED
                return
            
    def to_dict(self):
        return {
            "tasks": [task.to_dict() for task in self._tasks]
        }


    def cancel_task(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                task.status = TaskStatus.CANCELLED
                return

    def save(self, filename):
        data = [task.to_dict() for task in self._tasks]
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)


    def load(self, filepath):
        tasks = load_tasks(filepath)
        self._tasks = tasks
        
    def get(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None


