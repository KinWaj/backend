from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import supabase, SUPABASE_URL, SUPABASE_ANON_KEY
from supabase import create_client, Client
from schemas import UserAuth

from infrastructure.middleware.rateLimit import limiter
from schemas import LoginResponse

router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer(auto_error=False)

@router.post('/register', status_code=201)
async def register(request: Request, user_data: UserAuth):
    import re
    v = user_data.password
    if len(v) < 8:
        raise HTTPException(400, 'Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', v):
        raise HTTPException(400, 'Password must contain an uppercase letter')
    if not re.search(r'[a-z]', v):
        raise HTTPException(400, 'Password must contain a lowercase letter')
    if not re.search(r'[0-9]', v):
        raise HTTPException(400, 'Password must contain a digit')
    if not re.search(r'[^A-Za-z0-9]', v):
        raise HTTPException(400, 'Password must contain a special character')
    weak = ['123', 'password', 'abc', '1234', 'qwerty']
    if v.lower() in weak:
        raise HTTPException(400, 'Password too weak')
    try:
        response = supabase.auth.sign_up({
            'email': user_data.email,
            'password': user_data.password
        })
        user_obj = response.user
        token = getattr(response.session, 'access_token', None) if hasattr(response, 'session') else None
        user_id = user_obj.id if hasattr(user_obj, 'id') else user_obj.get('id')
        user_email = user_obj.email if hasattr(user_obj, 'email') else user_obj.get('email')
        role = 'user'
        try:
            profile_response = supabase.table('profiles').select('role').eq('id', user_id).execute()
            if profile_response.data and 'role' in profile_response.data[0]:
                role = profile_response.data[0]['role']
        except Exception:
            pass
        user_data_out = {
            'id': user_id,
            'email': user_email,
            'role': role
        }
        return {'token': token, 'user': user_data_out}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post('/login', response_model=LoginResponse)
@limiter.limit("7/minute")
async def login(request: Request, user_data: UserAuth):
    max_body_size = 1024 * 1024  # 1MB
    body = await request.body()
    try:
        response = supabase.auth.sign_in_with_password({
            'email': user_data.email,
            'password': user_data.password
        })
        user_obj = response.user
        user_id = user_obj.id if hasattr(user_obj, 'id') else user_obj.get('id')
        user_email = user_obj.email if hasattr(user_obj, 'email') else user_obj.get('email')
        role = 'user'
        try:
            profile_response = supabase.table('profiles').select('role').eq('id', user_id).execute()
            if profile_response.data and 'role' in profile_response.data[0]:
                role = profile_response.data[0]['role']
        except Exception:
            pass
        user_data_out = {
            'id': user_id,
            'email': user_email,
            'role': role
        }
        return LoginResponse(token=response.session.access_token, user=user_data_out)
    except Exception as e:
        raise HTTPException(401, 'Invalid credentials')

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials is None or not credentials.credentials:
        raise HTTPException(401, 'Not authenticated')
    try:
        user = supabase.auth.get_user(credentials.credentials)
        return user
    except Exception:
        raise HTTPException(401, 'Invalid token')


def get_authenticated_supabase(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Client:
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    client.postgrest.auth(credentials.credentials)
    return client