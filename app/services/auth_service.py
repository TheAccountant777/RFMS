import secrets
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.invitation import Invitation
from app.schemas.invitation import InvitationCreate
from app.services.email_service import email_service
from app.exceptions import ConflictError # Assuming a custom exception for conflicts

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
                Invitation.status == "PENDING" # Check for pending status
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
        # In a production system, you might enqueue this to a background worker (e.g., arq)
        try:
            await email_service.send_invitation_email(email, token)
        except Exception as e:
            # Log the email sending failure, but don't necessarily fail the invitation creation
            print(f"Failed to send invitation email to {email}: {e}")
            # Depending on requirements, you might want to mark the invitation as 'email_failed'
            # or have a separate process to retry sending emails.

        return db_invitation

# Note: AuthService instances should be created per request to manage the DB session.
# This class is not instantiated globally like EmailService.