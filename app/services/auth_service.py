import secrets
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from uuid import UUID

from app.models.invitation import Invitation, InvitationStatus
from app.models.user import User
from app.models.referral_link import ReferralLink
from app.schemas.invitation import InvitationCreate
from app.schemas.user import UserCreate
from app.schemas.auth import JWTTokens
from app.services.email_service import email_service
from app.core.security import hash_password, create_access_token, create_refresh_token, generate_unique_code
from app.exceptions import ConflictError, NotFoundError, ValidationError

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_invitation(self, email: str):
        """
        Creates a new invitation record and sends an invitation email.
        Raises ConflictError if an active invitation already exists for the email.
        """
        # Check if an active invitation already exists
        existing_invitation = await self.db.execute(
            select(Invitation).where(
                Invitation.email == email,
                Invitation.status == InvitationStatus.PENDING
            )
        )
        if existing_invitation.scalar_one_or_none():
            raise ConflictError(f"An active invitation already exists for {email}")

        # Generate a unique token
        token = secrets.token_urlsafe(32) # Generate a secure, URL-safe token

        # Calculate expiry date (e.g., 7 days from now)
        expires_at = datetime.utcnow() + timedelta(days=7)

        # Create the invitation record
        invitation_create = InvitationCreate(email=email, token=token, expires_at=expires_at)
        db_invitation = Invitation(**invitation_create.model_dump())

        self.db.add(db_invitation)
        await self.db.commit()
        await self.db.refresh(db_invitation)

        # Send the invitation email asynchronously (fire and forget or handle separately)
        # For simplicity in this example, we'll call it directly.
        try:
            await email_service.send_invitation_email(email, token)
        except Exception as e:
            # Log the email sending failure, but don't necessarily fail the invitation creation
            print(f"Failed to send invitation email to {email}: {e}")
            # Depending on requirements, you might want to mark the invitation as 'email_failed'
            # or have a separate process to retry sending emails.

        return db_invitation
    
    async def register_participant(self, invitation_token: str, user_data: UserCreate):
        """
        Registers a new participant using an invitation token.
        
        Args:
            invitation_token: The token from the invitation email
            user_data: The user registration data
            
        Returns:
            JWTTokens: Access and refresh tokens for the new user
            
        Raises:
            NotFoundError: If the invitation token is invalid, expired, or already used
            ConflictError: If the phone number is already registered
            ValidationError: If the data fails validation
        """
        # Find and validate the invitation
        invitation_result = await self.db.execute(
            select(Invitation).where(
                Invitation.token == invitation_token,
                Invitation.status == InvitationStatus.PENDING,
                Invitation.expires_at > datetime.utcnow()
            )
        )
        invitation = invitation_result.scalar_one_or_none()
        
        if not invitation:
            raise NotFoundError("Invalid or expired invitation token")
        
        # Check if phone number is already registered
        existing_user_result = await self.db.execute(
            select(User).where(User.phone_number == user_data.phone_number)
        )
        if existing_user_result.scalar_one_or_none():
            raise ConflictError("Phone number is already registered")
        
        # Start a transaction for creating user and referral link
        # Hash the password
        password_hash = hash_password(user_data.password)
        
        # Create the user record
        new_user = User(
            full_name=user_data.full_name,
            email=invitation.email,  # Use the email from the invitation
            password_hash=password_hash,
            phone_number=user_data.phone_number
        )
        
        self.db.add(new_user)
        await self.db.flush()  # Flush to get the user ID
        
        # Generate a unique referral code
        unique_code = generate_unique_code()
        
        # Check if code already exists (unlikely but possible)
        while True:
            existing_code_result = await self.db.execute(
                select(ReferralLink).where(ReferralLink.unique_code == unique_code)
            )
            if not existing_code_result.scalar_one_or_none():
                break
            unique_code = generate_unique_code()
        
        # Create the referral link
        new_referral_link = ReferralLink(
            user_id=new_user.id,
            unique_code=unique_code
        )
        
        self.db.add(new_referral_link)
        
        # Update invitation status to ACCEPTED
        await self.db.execute(
            update(Invitation)
            .where(Invitation.id == invitation.id)
            .values(status=InvitationStatus.ACCEPTED)
        )
        
        # Commit the transaction
        await self.db.commit()
        await self.db.refresh(new_user)
        
        # Generate JWT tokens
        access_token = create_access_token(data={"sub": str(new_user.id)})
        refresh_token = create_refresh_token(data={"sub": str(new_user.id)})
        
        return JWTTokens(
            access_token=access_token,
            refresh_token=refresh_token
        )

# Note: AuthService instances should be created per request to manage the DB session.
# This class is not instantiated globally like EmailService.