import sendgrid
from sendgrid.helpers.mail import Mail

sg = sendgrid.SendGridAPIClient(api_key="")
message = Mail(
    from_email="",
    to_emails="",
    subject="Test Email",
    plain_text_content="This is a test email."
)
try:
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(f"Error: {e}")
