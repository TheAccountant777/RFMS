# Import all models here so they are registered with SQLAlchemy's metadata
from .user import User
from .admin_user import AdminUser
from .invitation import Invitation
from .referral_link import ReferralLink
from .referral import Referral
from .payment import Payment
from .earning import Earning

# Optional: define __all__ for explicit imports
__all__ = [
    "User",
    "AdminUser",
    "Invitation",
    "ReferralLink",
    "Referral",
    "Payment",
    "Earning",
]
