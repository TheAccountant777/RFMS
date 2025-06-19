from fastapi import APIRouter

from .admin import invitations as admin_invitations_router # Import the admin invitations router

api_router = APIRouter()

# Include the admin invitations router
api_router.include_router(admin_invitations_router.router)

# You would include other routers for v1 here as they are created
# api_router.include_router(participant_router.router)
# api_router.include_router(auth_router.router)