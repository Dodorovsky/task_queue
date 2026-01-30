from task_queue.task import TaskStatus
from task_queue.storage import save_tasks, load_tasks
 
class QueueManager:
    def __init__(self):
        self._tasks = []

    def add_task(self, task):
        self._tasks.append(task)

    def get_all_tasks(self):
        return list(self._tasks)

    def get_next_task(self):
        for task in self._tasks:
            if task.status == TaskStatus.PENDING:
                return task
        return None

    def mark_task_completed(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                task.status = TaskStatus.COMPLETED
                return

    def cancel_task(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                task.status = TaskStatus.CANCELLED
                return

    def save(self, filepath):
        save_tasks(self._tasks, filepath)

    def load(self, filepath):
        tasks = load_tasks(filepath)
        self._tasks = tasks



