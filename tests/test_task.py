# tests/test_task.py
import pytest
from task import Task, TaskStatus
 
def test_task_initial_state():
    t = Task("Test task")
    assert t.description == "Test task"
    assert t.status == TaskStatus.PENDING
    assert t.id is not None
    assert t.created_at is not None

def test_start_task():
    t = Task("Do something")
    t.start()
    assert t.status == TaskStatus.PROCESSING


def test_start_invalid_state():
    t = Task("Do something")
    t.start()
    with pytest.raises(ValueError):
        t.start()  # no se puede empezar dos veces


def test_complete_task():
    t = Task("Finish this")
    t.complete()
    assert t.status == TaskStatus.COMPLETED


def test_complete_from_processing():
    t = Task("Finish this")
    t.start()
    t.complete()
    assert t.status == TaskStatus.COMPLETED


def test_complete_invalid_state():
    t = Task("Finish this")
    t.cancel()
    with pytest.raises(ValueError):
        t.complete()
 

def test_cancel_task():
    t = Task("Cancel me")
    t.cancel()
    assert t.status == TaskStatus.CANCELLED


def test_cancel_completed_task():
    t = Task("Done already")
    t.complete()
    with pytest.raises(ValueError):
        t.cancel()
