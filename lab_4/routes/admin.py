from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user, get_authenticated_supabase
from supabase import Client
from database import supabase as admin_supabase

router = APIRouter(prefix='/admin', tags=['admin'])

async def require_admin(user = Depends(get_current_user)):
    profile_response = admin_supabase.table('profiles').select('role').eq('id', user.user.id).execute()
    
    if not profile_response.data or profile_response.data[0].get('role') != 'admin':
        raise HTTPException(403, detail={'error': 'Admin access required'})
    
    return user

@router.get('/users')
async def get_all_users(
    user = Depends(require_admin),
    supabase: Client = Depends(get_authenticated_supabase)
):
    response = supabase.table('profiles').select('id, email, role, created_at').execute()
    return response.data

@router.delete('/users/{user_id}', status_code=204)
async def delete_user(
    user_id: str,
    user = Depends(require_admin),
    supabase: Client = Depends(get_authenticated_supabase)
):
    check_response = admin_supabase.table('profiles').select('id').eq('id', user_id).execute()
    
    if not check_response.data:
        raise HTTPException(404, detail={'error': 'User not found'})
    
    response = supabase.table('profiles').delete().eq('id', user_id).execute()
    
    try:
        admin_supabase.auth.admin.delete_user(user_id)
    except Exception:
        pass
    
    return None