from fastapi import APIRouter, HTTPException, Depends
from database import supabase
from schemas import TaskCreate, TaskUpdate, Task
from auth import get_current_user




router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get('/')
async def get_tasks(user = Depends(get_current_user)):
    response = supabase.table('tasks').select('*').order(
        'created_at', desc=True).execute()
    return response.data


@router.post('/', status_code=201)
async def create_task(task: TaskCreate, user = Depends(get_current_user)):
    response = supabase.table('tasks').insert(
        {'title': task.title}).execute()
    return response.data[0]


@router.patch('/{task_id}')
async def update_task(task_id: str, task: TaskUpdate,
                      user = Depends(get_current_user)):
    response = supabase.table('tasks').update(
        {'completed': task.completed}).eq('id', task_id).execute()
    if not response.data:
        raise HTTPException(404, 'Task not found')
    return response.data[0]


@router.delete('/{task_id}', status_code=204)
async def delete_task(task_id: str, user = Depends(get_current_user)):
    supabase.table('tasks').delete().eq('id', task_id).execute()
    return None
