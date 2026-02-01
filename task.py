from datetime import datetime
import uuid
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Task:
    def __init__(self, description, priority=TaskPriority.MEDIUM):
        self.id = str(uuid.uuid4())
        self.description = description
        self.priority = priority

        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        self.completed_at = None
        self.cancelled_at = None
        self.processing_started_at = None

        # IMPORTANT: initialize internal status without triggering setter
        self._status = TaskStatus.PENDING

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        self._status = new_status
        self.updated_at = datetime.utcnow()

        if new_status == TaskStatus.COMPLETED:
            self.completed_at = datetime.utcnow()

        if new_status == TaskStatus.CANCELLED:
            self.cancelled_at = datetime.utcnow()

        if new_status == TaskStatus.PROCESSING:
            self.processing_started_at = datetime.utcnow()

    def start(self):
        if self.status != TaskStatus.PENDING:
            raise ValueError("Only pending tasks can be started")
        self.status = TaskStatus.PROCESSING

    def complete(self):
        if self.status not in (TaskStatus.PENDING, TaskStatus.PROCESSING):
            raise ValueError("Only pending or processing tasks can be completed")
        self.status = TaskStatus.DONE

    def cancel(self):
        if self.status == TaskStatus.DONE:
            raise ValueError("Cannot cancel a completed task")
        self.status = TaskStatus.CANCELLED

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "processing_started_at": self.processing_started_at.isoformat() if self.processing_started_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(
            description=data["description"],
            priority=TaskPriority(data["priority"])
        )
        task.id = data["id"]
        task._status = TaskStatus(data["status"])
        task.created_at = datetime.fromisoformat(data["created_at"])
        task.updated_at = datetime.fromisoformat(data["updated_at"])
        task.completed_at = datetime.fromisoformat(data["completed_at"]) if data["completed_at"] else None
        task.cancelled_at = datetime.fromisoformat(data["cancelled_at"]) if data["cancelled_at"] else None
        task.processing_started_at = datetime.fromisoformat(data["processing_started_at"]) if data["processing_started_at"] else None
        return task
