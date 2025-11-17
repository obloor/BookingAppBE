import logging
from datetime import timedelta
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)

def send_email(to_email, subject, html_content, from_email=None):
    if not from_email:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@reservationapp.com')

    logger.info(f"Attempting to send email to: {to_email}, Subject: {subject}")
    logger.info(f"Using From Email: {from_email}")

    if not hasattr(settings, 'SENDGRID_API_KEY') or not settings.SENDGRID_API_KEY:
        error_msg = "SENDGRID_API_KEY is not set in settings"
        logger.error(error_msg)
        return False, error_msg
    
    try:
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        logger.info(f"Connecting to SendGrid with API key: {settings.SENDGRID_API_KEY[:5]}...")
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        
        logger.info("Sending email...")
        response = sg.send(message)
        
        logger.info(f"Email sent successfully! Status: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        
        return True, f"Email sent successfully (Status: {response.status_code})"
        
    except Exception as e:
        error_msg = f"Error sending email to {to_email}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg

def schedule_reminder(reservation):

    from django.utils import timezone
    from django.template.loader import render_to_string
    # Reminder is set 1 hour before the reservation start
    reminder_time = reservation.start_time - timedelta(hours=1)
    current_time = timezone.now()
    
    if current_time < reminder_time:
        logger.info(f"Would send reminder for reservation {reservation.id} at {reminder_time}")
        

        context = {
            'user': reservation.booked_by,
            'reservation': reservation,
            'time': reservation.start_time,
            'duration': (reservation.end_time - reservation.start_time).total_seconds() / 3600,
        }
        
        subject = f"Reminder: Upcoming Reservation - {reservation.room.name}"
        html_content = render_to_string('reservations/emails/reminder.html', context)
        
