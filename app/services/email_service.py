import httpx
from app.config import settings

class EmailService:
    def __init__(self):
        self.api_key = settings.resend_api_key # Use lowercase attribute name
        self.base_url = "https://api.resend.com"
        self.client = httpx.AsyncClient(base_url=self.base_url)
        self.sender_email = "onboarding@resend.dev" # Replace with a verified sender domain if available

    async def send_invitation_email(self, to_email: str, token: str):
        """
        Sends a referral program invitation email using Resend.
        """
        if not self.api_key:
            print("Resend API key not configured. Skipping email sending.")
            # In a real application, you might want to log this or raise a specific error
            return

        registration_url = f"{settings.referral_base_url}/register?token={token}" # Use lowercase attribute name

        email_data = {
            "from": f"{settings.project_name} <{self.sender_email}>", # Use lowercase attribute name
            "to": [to_email],
            "subject": f"You're Invited to the {settings.project_name} Referral Program!", # Use lowercase attribute name
            "html": f"""
                <p>Hello,</p>
                <p>You've been invited to join the {settings.project_name} Referral Program.</p>
                <p>Click the link below to register and start referring:</p>
                <p><a href="{registration_url}">{registration_url}</a></p>
                <p>This invitation link will expire soon.</p>
                <p>Best regards,</p>
                <p>The {settings.project_name} Team</p>
            """
        }

        try:
            response = await self.client.post(
                "/emails",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=email_data
            )
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            print(f"Invitation email sent successfully to {to_email}")
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error sending email: {e}")
            # Log the error details (e.g., response.text) in a real application
            raise # Re-raise the exception after logging
        except httpx.RequestError as e:
            print(f"Request error sending email: {e}")
            raise # Re-raise the exception after logging

# Instantiate the service
email_service = EmailService()