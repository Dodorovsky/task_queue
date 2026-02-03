import pytest
from task_queue.task import Task, TaskPriority, TaskStatus
from task_queue.queue_manager import QueueManager


def test_task_has_default_priority():
    task = Task("Test")
    assert task.priority == TaskPriority.MEDIUM


def test_set_task_priority():
    task = Task("Important", priority=TaskPriority.HIGH)
    assert task.priority == TaskPriority.HIGH


def test_queue_returns_high_priority_first(tmp_path):
    filepath = tmp_path / "tasks.json"
    manager = QueueManager(str(filepath))

    # Crear tareas usando la API actual
    manager.add_task("Low", TaskPriority.LOW)
    manager.add_task("High", TaskPriority.HIGH)
    manager.add_task("Medium", TaskPriority.MEDIUM)

    next_task = manager.get_next_task()

    assert next_task.description == "High"
    assert next_task.priority == TaskPriority.HIGH



def test_queue_respects_fifo_within_same_priority(tmp_path):
    filepath = tmp_path / "tasks.json"
    manager = QueueManager(str(filepath))

    # Crear tareas usando la API actual
    manager.add_task("First", TaskPriority.HIGH)
    manager.add_task("Second", TaskPriority.HIGH)

    next_task = manager.get_next_task()

    assert next_task.description == "First"

