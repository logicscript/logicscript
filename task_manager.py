"""
Task Management System

Implemented from LogicScript specification:
- SHAPE Task with id, title, done, createdAt fields
- FUNC addTask(title) - create a new task
- FUNC completeTask(taskId) - mark task as done
- QUERY openTasks - retrieve all incomplete tasks
"""

from __future__ import print_function
import uuid
from datetime import datetime
try:
    from typing import Optional
except ImportError:
    Optional = None


class Task:
    """Task data shape matching LogicScript SHAPE definition."""
    
    def __init__(self, title, task_id=None, done=False, created_at=None):
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.done = done
        self.createdAt = created_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "createdAt": self.createdAt.isoformat()
        }
    
    def __repr__(self):
        return "Task(id=%r, title=%r, done=%r)" % (self.id, self.title, self.done)


# In-memory task store (simulates database)
_task_store = {}


def addTask(title):
    """
    FUNC addTask(title)
    VALIDATE title not empty
    DO task = Task.create(title)
    RETURN task
    """
    # VALIDATE: title not empty
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")
    
    title = title.strip()
    
    # VALIDATE: title max length
    if len(title) > 200:
        raise ValueError("Title cannot exceed 200 characters")
    
    # DO: create task
    task = Task(title=title)
    _task_store[task.id] = task
    
    return task


def completeTask(taskId):
    """
    FUNC completeTask(taskId)
    VALIDATE taskId exists in Task
    VALIDATE task.done IS false
    DO task.done = true
    RETURN task
    """
    # VALIDATE: taskId exists in Task
    if taskId not in _task_store:
        raise ValueError("Task with id '%s' does not exist" % taskId)
    
    task = _task_store[taskId]
    
    # VALIDATE: task.done IS false
    if task.done:
        raise ValueError("Task '%s' is already completed" % taskId)
    
    # DO: mark task as done
    task.done = True
    
    return task


def openTasks():
    """
    QUERY openTasks
    FROM Task
    WHERE done IS false
    ORDER BY createdAt ASC
    """
    # Filter incomplete tasks and sort by creation date
    tasks = [t for t in _task_store.values() if not t.done]
    tasks.sort(key=lambda t: t.createdAt)
    
    return tasks


def get_task(taskId):
    """Retrieve a task by ID."""
    return _task_store.get(taskId)


def list_all_tasks():
    """List all tasks (for debugging)."""
    return list(_task_store.values())


def clear_all_tasks():
    """Clear all tasks (for testing)."""
    _task_store.clear()


# Example usage
if __name__ == "__main__":
    # Create a task
    task1 = addTask("Learn LogicScript")
    print("Created: %s" % task1)
    
    task2 = addTask("Build a todo app")
    print("Created: %s" % task2)
    
    # List open tasks
    print("\nOpen tasks: %s" % openTasks())
    
    # Complete a task
    completed = completeTask(task1.id)
    print("Completed: %s" % completed)
    
    # List open tasks again
    print("\nOpen tasks after completion: %s" % openTasks())