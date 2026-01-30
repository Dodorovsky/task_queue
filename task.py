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
