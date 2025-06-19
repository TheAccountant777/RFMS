# Import all schemas here for easy access
from .user import UserBase, UserCreate, UserUpdate, UserResponse
from .admin_user import AdminUserBase, AdminUserCreate, AdminUserUpdate, AdminUserResponse
from .invitation import InvitationBase, InvitationCreate, InvitationResponse
from .referral import ReferralLinkBase, ReferralLinkCreate, ReferralLinkResponse, ReferralBase, ReferralCreate, ReferralResponse, ParticipantStatsResponse
from .payment import PaymentBase, PaymentCreate, PaymentResponse
from .earning import EarningBase, EarningCreate, EarningResponse
from .auth import LoginPayload, JWTTokens, ParticipantRegisterPayload, RefreshPayload
from .conversion import ConversionPayload

# Optional: define __all__
__all__ = [
    # User Schemas
    "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    # Admin User Schemas
    "AdminUserBase", "AdminUserCreate", "AdminUserUpdate", "AdminUserResponse",
    # Invitation Schemas
    "InvitationBase", "InvitationCreate", "InvitationResponse",
    # Referral Schemas
    "ReferralLinkBase", "ReferralLinkCreate", "ReferralLinkResponse",
    "ReferralBase", "ReferralCreate", "ReferralResponse",
    "ParticipantStatsResponse",
    # Payment Schemas
    "PaymentBase", "PaymentCreate", "PaymentResponse",
    # Earning Schemas
    "EarningBase", "EarningCreate", "EarningResponse",
    # Auth Schemas
    "LoginPayload", "JWTTokens", "ParticipantRegisterPayload", "RefreshPayload",
    # Conversion Schemas
    "ConversionPayload",
]
