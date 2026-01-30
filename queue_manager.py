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



