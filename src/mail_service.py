import os
import gc
from config.settings import MAIL_CONFIG
from src.logger_manager import get_logger

log = get_logger("MailService")

class MailService:
    def __init__(self):
        self.user = MAIL_CONFIG['user']
        self.password = MAIL_CONFIG['pass']

    def send_report(self, attachment_path):
        log.info(f"Preparing to send report: {attachment_path}")
        return self._execute_send(
            MAIL_CONFIG['business_recipients'],
            f"REPORT: Network Monitoring - {os.path.basename(attachment_path)}",
            "Greetings,\n\nPlease find attached the automatically generated telephony log report.\n\nBest regards.",
            attachment_path
        )

    def send_error_alert(self, failed_step):
        log.info(f"Preparing to send error alert for step: {failed_step}")
        return self._execute_send(
            MAIL_CONFIG['support_recipients'],
            "ALERT: Automation Process Failure",
            f"The system failed during the following step: [{failed_step}]. Please check internal logs."
        )

    def _execute_send(self, recipients, subject, body, attachment=None):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders

        if len(recipients) > 15:
            log.error("Security safeguard: Recipient limit exceeded.")
            return False
        try:
            log.info(f"Connecting to SMTP server: {MAIL_CONFIG['server']}:{MAIL_CONFIG['port']}")
            message = MIMEMultipart()
            message['From'] = self.user
            message['To'] = ", ".join(recipients)
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            if attachment:
                log.info(f"Attaching file to email: {attachment}")
                with open(attachment, "rb") as file:
                    part = MIMEBase('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
                part.set_param('name', os.path.basename(attachment))
                message.attach(part)
                del part

            with smtplib.SMTP(MAIL_CONFIG['server'], MAIL_CONFIG['port']) as server:
                log.info("Starting TLS encryption.")
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.user, recipients, message.as_string())
            log.info("Email sent successfully.")
            
            del message
            gc.collect()
            return True
        except Exception as e:
            log.error(f"SMTP communication error: {e}")
            return False


