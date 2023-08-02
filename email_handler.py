import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "example@gmail.com"
smtp_password = "password"

def sendmail(username, user_email, image_url):
    message = MIMEMultipart()

    html_content = f"""
        <html>
            <head>
                <title>Alert: Door Opened</title>
            </head>
            <body>
                <p>Dear {username},</p>
                <p>Our door open sensor has detected that the door has been opened. Please check to ensure that you or someone you trust has opened the door. If you did not open the door, please take the necessary precautions to ensure your safety.</p>
                <img src="{image_url}" alt="door open icon" width="100%" height="100%">
                <p>If you have any concerns or questions, please contact us at [contact information].</p>
                <p>Best regards,</p>
                <p>Security System</p>
                
            </body>
        </html>
    """
    message.attach(MIMEText(html_content, "html"))
    message["From"] = smtp_username
    message["To"] = user_email
    message["Subject"] = "Alert Door Open"

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, message["To"], message.as_string())

    print("Email sent successfully!")
