from datetime import datetime
from task import Task, TaskStatus, TaskPriority


def test_task_has_created_at():
    task = Task("Test")
    assert isinstance(task.created_at, datetime)


def test_task_updates_updated_at_on_status_change():
    task = Task("Test")
    old_updated = task.updated_at

    task.status = TaskStatus.COMPLETED

    assert task.updated_at >= old_updated


def test_task_sets_completed_at_when_completed():
    task = Task("Test")
    task.status = TaskStatus.COMPLETED

    assert isinstance(task.completed_at, datetime)


def test_task_sets_cancelled_at_when_cancelled():
    task = Task("Test")
    task.status = TaskStatus.CANCELLED

    assert isinstance(task.cancelled_at, datetime)


def test_processing_sets_processing_started_at():
    task = Task("Test")
    task.status = TaskStatus.PROCESSING

    assert isinstance(task.processing_started_at, datetime)

