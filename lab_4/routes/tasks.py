from fastapi import APIRouter, HTTPException, Depends, Response, Request
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
    request: Request,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    content_type = request.headers.get('content-type', '')
    if 'application/json' not in content_type:
        raise HTTPException(400, 'Content-Type must be application/json')
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(400, 'Invalid JSON payload')
    from schemas import TaskCreate
    try:
        task = TaskCreate(**data)
    except Exception:
        raise HTTPException(400, 'Invalid task data')
    response = supabase.table('tasks').insert(
        {'title': task.title, 'user_id': user.user.id}).execute()
    return response.data[0]

@router.patch('/{task_id}')
async def update_task(
    task_id: str,
    request: Request,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    body = await request.json()
    update_data = {}
    if 'completed' in body:
        update_data['completed'] = body['completed']
    if 'title' in body:
        update_data['title'] = body['title']
    response = supabase.table('tasks').update(update_data).eq('id', task_id).execute()
    if not response.data:
        from database import supabase as admin_supabase
        check_response = admin_supabase.table('tasks').select('id').eq('id', task_id).execute()
        if not check_response.data:
            raise HTTPException(404, detail={'error': 'Task not found'})
        else:
            raise HTTPException(403, detail={'error': 'Access denied'})
    return response.data[0]

@router.options('/', include_in_schema=False)
async def options_tasks():
    return Response(status_code=204)



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

