def send_activation_email(email: str, token: str) -> None:
    # Temporary stub (MailHog/SMTP later)
    print(
        f"[EMAIL] Activation link for {email}: "
        f"http://localhost:8000/api/v1/accounts/activate?token={token}"
    )
