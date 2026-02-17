from task import TaskStatus
from storage import save_tasks, load_tasks
from task import Task, TaskPriority
import json
from datetime import datetime

 
class QueueManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self._tasks = self.load(filepath)

    def add_task(self, description, priority=TaskPriority.MEDIUM):
        task = Task(description, priority=priority)
        self._tasks.append(task)
        return task

    def get_all_tasks(self):
        return self._tasks


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
            
    def get_task(self, task_id: int):
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None
       
    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority.name,
            "status": self.status.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "processing_started_at": self.processing_started_at.isoformat() if self.processing_started_at else None,
            "parent_id": self.parent_id,  # ← NUEVO
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
        try:
            with open(filepath) as f:
                data = json.load(f)
        except FileNotFoundError:
            return []

        tasks = []
        for item in data:
            task = Task(
                description=item["description"],
                priority=item["priority"],
                status=item["status"],
                parent_id=item.get("parent_id"),
                id=item["id"],
                created_at=item.get("created_at"),
                updated_at=item.get("updated_at"),
                completed_at=item.get("completed_at"),
                cancelled_at=item.get("cancelled_at"),
                processing_started_at=item.get("processing_started_at")
            )
            tasks.append(task)

        return tasks

    def add_task_with_subtasks(self, description, priority, subtasks_descriptions):
        # 1. Crear tarea principal
        main_task = Task(description=description, priority=priority, parent_id=None)
        self._tasks.append(main_task)

        # 2. Crear subtareas
        for sub_desc in subtasks_descriptions:
            subtask = Task(description=sub_desc, priority=priority, parent_id=main_task.id)
            self._tasks.append(subtask)

        # 3. Guardar
        self.save(self.filepath)

        return main_task.id

    def get(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None
        
    def delete_task(self, task_id: int):
        # borrar la tarea
        self._tasks = [t for t in self._tasks if t.id != task_id]

        # borrar subtareas asociadas
        self._tasks = [t for t in self._tasks if t.parent_id != task_id]

        self.save(self.filepath)

    def mark_task_done(self, task_id: str):
        for task in self._tasks:
            if task.id == task_id:
                task.status = TaskStatus.DONE
                break
        self.save(self.filepath)
        
    def mark_task_undone(self, task_id: str):
        for task in self._tasks:
            if task.id == task_id:
                task.status = TaskStatus.PENDING
                break
        self.save(self.filepath)

    def purge(self):
        before = len(self._tasks)
        self._tasks = [
            t for t in self._tasks
            if t.status not in (TaskStatus.COMPLETED, TaskStatus.CANCELLED)
        ]
        after = len(self._tasks)

        self.save(self.filepath)

        return before - after
    
    def update_task_priority(self, task_id: str, new_priority: str):
        for task in self._tasks:
            if task.id == task_id:
                task.priority = TaskPriority[new_priority]  # usa tu enum
                break
        self.save(self.filepath)


