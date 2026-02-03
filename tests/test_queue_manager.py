import pytest
import os
from task_queue.task import Task, TaskStatus, TaskPriority
from task_queue.queue_manager import QueueManager

def test_add_task(tmp_path):
    filepath = tmp_path / "tasks.json"
    manager = QueueManager(str(filepath))

    manager.add_task("Test task", TaskPriority.LOW)

    tasks = manager.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0].description == "Test task"
    assert tasks[0].status == TaskStatus.PENDING



def test_get_next_task_returns_first_pending(tmp_path):
    filepath = tmp_path / "tasks.json"
    manager = QueueManager(str(filepath))

    # Creamos las tareas usando la API actual
    manager.add_task("Task 1", TaskPriority.LOW)
    manager.add_task("Task 2", TaskPriority.LOW)
    manager.add_task("Task 3", TaskPriority.LOW)

    # Marcamos la primera como COMPLETED
    manager._tasks[0].status = TaskStatus.COMPLETED
    manager.save(str(filepath))

    next_task = manager.get_next_task()

    assert next_task.description == "Task 2"
    assert next_task.status == TaskStatus.PENDING



def test_mark_task_completed(tmp_path):
    filepath = tmp_path / "tasks.json"
    manager = QueueManager(str(filepath))

    # Crear la tarea usando la API actual
    manager.add_task("Complete me", TaskPriority.LOW)
    task = manager.get_all_tasks()[0]

    # Ejecutar la acción
    manager.mark_task_completed(task.id)

    # Recargar la tarea desde el manager
    updated_task = manager.get_all_tasks()[0]

    assert updated_task.status == TaskStatus.COMPLETED


 
def test_cancel_task(tmp_path):
    filepath = tmp_path / "tasks.json"
    manager = QueueManager(str(filepath))

    # Crear la tarea usando la API actual
    manager.add_task("Cancel me", TaskPriority.LOW)
    task = manager.get_all_tasks()[0]

    # Ejecutar la acción
    manager.cancel_task(task.id)

    # Recargar la tarea desde el manager
    updated_task = manager.get_all_tasks()[0]

    assert updated_task.status == TaskStatus.CANCELLED



def test_mark_task_completed_nonexistent_id(tmp_path):
    filepath = tmp_path / "tasks.json"
    manager = QueueManager(str(filepath))

    # Should not raise an exception
    manager.mark_task_completed("nonexistent-id")

    assert True  # If we reach here, the test passes



def test_cancel_task_nonexistent_id(tmp_path):
    filepath = tmp_path / "tasks.json"
    manager = QueueManager(str(filepath))

    # Should not raise an exception
    manager.cancel_task("nonexistent-id")

    assert True



def test_get_next_task_when_no_pending(tmp_path):
    filepath = tmp_path / "tasks.json"
    manager = QueueManager(str(filepath))

    # Crear una tarea COMPLETED usando la API actual
    manager.add_task("Done", TaskPriority.LOW)
    manager._tasks[0].status = TaskStatus.COMPLETED
    manager.save(str(filepath))

    assert manager.get_next_task() is None



def test_queue_manager_save_and_load(tmp_path):
    filepath = tmp_path / "queue.json"

    # Crear manager con filepath
    manager = QueueManager(str(filepath))

    # Crear tareas usando la API actual
    manager.add_task("Task 1", TaskPriority.LOW)
    manager.add_task("Task 2", TaskPriority.LOW)

    # Marcar la segunda como COMPLETED
    manager._tasks[1].status = TaskStatus.COMPLETED

    # Guardar usando el filepath correcto
    manager.save(str(filepath))

    # Nuevo manager debe cargar automáticamente desde el mismo archivo
    new_manager = QueueManager(str(filepath))

    tasks = new_manager.get_all_tasks()

    assert len(tasks) == 2
    assert tasks[0].description == "Task 1"
    assert tasks[0].status == TaskStatus.PENDING
    assert tasks[1].description == "Task 2"
    assert tasks[1].status == TaskStatus.COMPLETED




def test_queue_manager_load_missing_file(tmp_path):
    filepath = tmp_path / "missing.json"

    manager = QueueManager(str(filepath))  # ahora requiere filepath
    manager.load(str(filepath))            # cargar archivo inexistente

    assert manager.get_all_tasks() == []

