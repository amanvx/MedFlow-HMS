import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


class EmailService:
    
    @staticmethod
    def send_email(to_email, subject, body, is_html=False):
        
        try:
            # Get config
            smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            sender_email = current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                current_app.logger.warning("Email credentials not configured")
                return False
            
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = sender_email
            message['To'] = to_email
            message['Subject'] = subject
            
            # Attach body
            mime_type = 'html' if is_html else 'plain'
            message.attach(MIMEText(body, mime_type))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            current_app.logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")
            return False
    
    @staticmethod
    def send_appointment_reminder(appointment):
        
        patient_email = appointment.patient.user.email
        doctor_name = appointment.doctor.user.full_name
        appointment_time = appointment.appointment_dt.strftime('%Y-%m-%d %H:%M')
        
        subject = "Appointment Reminder - Hospital Management System"
        body = f"""
            <html>
                <body>
                    <p>Dear {appointment.patient.user.full_name},</p>
                    <p>This is a reminder for your upcoming appointment:</p>
                    <ul>
                        <li><strong>Doctor:</strong> {doctor_name}</li>
                        <li><strong>Date & Time:</strong> {appointment_time}</li>
                    </ul>
                    <p>Please arrive 10 minutes early. If you have any questions, contact us.</p>
                    <p>Thank you,<br>Hospital Management System</p>
                </body>
            </html>
            """
        
        return EmailService.send_email(patient_email, subject, body, is_html=True)
    
    @staticmethod
    def send_welcome_email(user):
        
        subject = "Welcome to Hospital Management System"
        body = f"""
            <html>
                <body>
                    <p>Dear {user.full_name},</p>
                    <p>Welcome to the Hospital Management System! We are glad to have you on board.</p>
                    <p>If you have any questions or need assistance, feel free to contact our support team.</p>
                    <p>Best regards,<br>Hospital Management System</p>
                </body>
            </html>
            """
        
        return EmailService.send_email(user.email, subject, body, is_html=True)
