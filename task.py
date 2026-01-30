# task.py
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    


@dataclass
class Task:
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)

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
  