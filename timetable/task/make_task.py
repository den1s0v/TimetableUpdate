from asgiref.sync import sync_to_async

from timetable.models import Task
from timetable.task.clear_storage import task_clear
from timetable.task.snapshot import task_make_snapshot


async def make_task(task:Task):
    action = task.params.get('action', None)
    match action:
        case 'make_new':
            await task_make_snapshot(task)
        case 'dell':
            await sync_to_async(task_clear)(task)
