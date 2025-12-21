from fastapi import APIRouter, HTTPException, Depends
from schemas import TaskCreate, TaskUpdate, Task
from auth import get_current_user, get_authenticated_supabase
from supabase import Client

router = APIRouter(prefix='/tasks', tags=['tasks'])

@router.get('/')
async def get_tasks(
    user = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    response = supabase.table('tasks').select('*').order(
        'created_at', desc=True).execute()
    return response.data

@router.post('/', status_code=201)
async def create_task(
    task: TaskCreate, 
    user = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    response = supabase.table('tasks').insert(
        {'title': task.title}).execute()
    return response.data[0]

@router.patch('/{task_id}')
async def update_task(
    task_id: str, 
    task: TaskUpdate,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):

    response = supabase.table('tasks').update(
        {'completed': task.completed}
    ).eq('id', task_id).execute()
    

    if not response.data:

        from database import supabase as admin_supabase
        check_response = admin_supabase.table('tasks').select('id').eq('id', task_id).execute()
        
        if not check_response.data:
            raise HTTPException(404, detail={'error': 'Task not found'})
        else:
            raise HTTPException(401, detail={'error': 'Unauthorized'})
    
    return response.data[0]

@router.delete('/{task_id}', status_code=204)
async def delete_task(
    task_id: str, 
    user = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):

    response = supabase.table('tasks').delete().eq('id', task_id).execute()
    

    if not response.data:

        from database import supabase as admin_supabase
        check_response = admin_supabase.table('tasks').select('id').eq('id', task_id).execute()
        
        if not check_response.data:
            raise HTTPException(404, detail={'error': 'Task not found'})
        else:
            raise HTTPException(403, detail={'error': 'Access denied'})
    
    return None