import sendgrid
from sendgrid.helpers.mail import Mail

sg = sendgrid.SendGridAPIClient(api_key="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")
message = Mail(
    from_email="muazashraf456@gmail.com",
    to_emails="muazashraf1998@gmail.com",
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
