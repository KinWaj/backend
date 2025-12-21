from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import supabase, SUPABASE_URL, SUPABASE_ANON_KEY
from supabase import create_client, Client
from schemas import UserAuth

router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()

@router.post('/register', status_code=201)
async def register(user_data: UserAuth):
    try:
        response = supabase.auth.sign_up({
            'email': user_data.email,
            'password': user_data.password
        })
        return {'message': 'User created', 'user': response.user}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post('/login')
async def login(user_data: UserAuth):
    try:
        response = supabase.auth.sign_in_with_password({
            'email': user_data.email,
            'password': user_data.password
        })
        return {
            'token': response.session.access_token,
            'user': response.user
        }
    except Exception as e:
        raise HTTPException(401, 'Invalid credentials')

# Get current user info
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        return user
    except Exception:
        raise HTTPException(401, 'Invalid token')

# NEW: Get authenticated Supabase client
def get_authenticated_supabase(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Client:
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    client.postgrest.auth(credentials.credentials)
    return client