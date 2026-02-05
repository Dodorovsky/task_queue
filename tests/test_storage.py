import json
import os
from task import Task, TaskStatus
from storage import save_tasks, load_tasks
 

def test_save_and_load_tasks(tmp_path):
    filepath = tmp_path / "tasks.json"

    t1 = Task("Task 1")
    t2 = Task("Task 2")
    t2.status = TaskStatus.COMPLETED

    save_tasks([t1, t2], filepath)

    assert os.path.exists(filepath)

    loaded = load_tasks(filepath)

    assert len(loaded) == 2
    assert loaded[0].description == "Task 1"
    assert loaded[0].status == TaskStatus.PENDING
    assert loaded[1].description == "Task 2"
    assert loaded[1].status == TaskStatus.COMPLETED


def test_load_tasks_empty_file(tmp_path):
    filepath = tmp_path / "empty.json"
    filepath.write_text("[]")

    loaded = load_tasks(filepath)

    assert loaded == []


def test_load_tasks_missing_file(tmp_path):
    filepath = tmp_path / "missing.json"

    loaded = load_tasks(filepath)

    assert loaded == []  # Should not crash
