import firebase_functions as functions
from firebase_admin import initialize_app, firestore, messaging
import logging
import requests
import os
import json

# Initialize Firebase app
initialize_app()

# Configure logging
logger = functions.logger

@functions.firestore.on_document_created(document="outbreak_alerts/{alertId}")
def send_outbreak_notifications(event):
    """
    Cloud Function triggered when a new outbreak alert is created.
    Sends notifications to relevant stakeholders.
    """
    try:
        # Get the new alert data
        alert = event.data.to_dict()
        alert_id = event.document.id
        
        # Extract alert details
        alert_type = alert.get('alert_type')
        severity = alert.get('severity_level', 1)
        latitude = alert.get('latitude')
        longitude = alert.get('longitude')
        description = alert.get('description', 'New outbreak alert')
        
        if not all([alert_type, latitude, longitude]):
            logger.warning(f"Missing required data in alert {alert_id}")
            return
        
        # 1. Send FCM notifications to mobile app users
        send_fcm_notifications(alert_id, alert_type, severity, description, latitude, longitude)
        
        # 2. Send email notifications to administrators
        send_email_notifications(alert_id, alert_type, severity, description, latitude, longitude)
        
        # 3. Send webhook notifications to integrated systems
        send_webhook_notifications(alert_id, alert, latitude, longitude)
        
        # 4. Update alert status
        db = firestore.client()
        db.collection('outbreak_alerts').document(alert_id).update({
            'notification_sent': True,
            'notification_timestamp': firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Notifications sent for alert {alert_id}")
    
    except Exception as e:
        logger.error(f"Error in send_outbreak_notifications: {e}")

def send_fcm_notifications(alert_id, alert_type, severity, description, latitude, longitude):
    """Send Firebase Cloud Messaging notifications to mobile app users."""
    try:
        # Create the FCM message
        message = messaging.Message(
            topic=f'outbreaks-{alert_type}',
            notification=messaging.Notification(
                title=f"Alert: {alert_type.replace('_', ' ').title()} (Level {severity})",
                body=description
            ),
            data={
                'alert_id': alert_id,
                'alert_type': alert_type,
                'severity': str(severity),
                'latitude': str(latitude),
                'longitude': str(longitude)
            },
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='notification_icon',
                    color='#f45342'
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        badge=1,
                        sound='default'
                    )
                )
            )
        )
        
        # Send the message
        response = messaging.send(message)
        logger.info(f"FCM notification sent: {response}")
    
    except Exception as e:
        logger.error(f"Error sending FCM notification: {e}")

def send_email_notifications(alert_id, alert_type, severity, description, latitude, longitude):
    """Send email notifications to administrators."""
    try:
        # Get admin email addresses from environment or config
        admin_emails = os.environ.get('ADMIN_EMAILS', '').split(',')
        
        if not admin_emails or admin_emails[0] == '':
            logger.warning("No admin emails configured for notifications")
            return
        
        # Use a service like SendGrid, Mailgun, etc.
        email_api_key = os.environ.get('EMAIL_API_KEY')
        email_api_url = os.environ.get('EMAIL_API_URL')
        
        if not email_api_key or not email_api_url:
            logger.warning("Email API not configured")
            return
        
        # Prepare email content
        email_data = {
            'api_key': email_api_key,
            'to': admin_emails,
            'subject': f"MNTRK Alert: {alert_type.replace('_', ' ').title()} (Level {severity})",
            'html': f"""
                <h2>MNTRK Outbreak Alert</h2>
                <p><strong>Alert ID:</strong> {alert_id}</p>
                <p><strong>Type:</strong> {alert_type.replace('_', ' ').title()}</p>
                <p><strong>Severity:</strong> {severity}/5</p>
                <p><strong>Description:</strong> {description}</p>
                <p><strong>Location:</strong> {latitude}, {longitude}</p>
                <p><a href="https://mntrk-dashboard.example.com/alerts/{alert_id}">View in Dashboard</a></p>
            """
        }
        
        # Send the email
        response = requests.post(email_api_url, json=email_data)
        
        if response.status_code == 200:
            logger.info(f"Email notifications sent to {len(admin_emails)} recipients")
        else:
            logger.error(f"Failed to send email notifications: {response.status_code} - {response.text}")
    
    except Exception as e:
        logger.error(f"Error sending email notifications: {e}")

def send_webhook_notifications(alert_id, alert_data, latitude, longitude):
    """Send webhook notifications to integrated systems."""
    try:
        # Get webhook URLs from environment or config
        webhook_urls = json.loads(os.environ.get('WEBHOOK_URLS', '{}'))
        
        if not webhook_urls:
            logger.info("No webhook URLs configured")
            return
        
        # Prepare webhook payload
        payload = {
            'alert_id': alert_id,
            'alert_type': alert_data.get('alert_type'),
            'severity': alert_data.get('severity_level'),
            'description': alert_data.get('description'),
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'radius_km': alert_data.get('radius_km', 10)
            },
            'timestamp': alert_data.get('alert_timestamp').isoformat() if alert_data.get('alert_timestamp') else None,
            'status': alert_data.get('status')
        }
        
        # Send to each configured webhook
        for system_name, url in webhook_urls.items():
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [200, 201, 202]:
                    logger.info(f"Webhook notification sent to {system_name}: {response.status_code}")
                else:
                    logger.warning(f"Failed to send webhook to {system_name}: {response.status_code} - {response.text}")
            
            except Exception as e:
                logger.error(f"Error sending webhook to {system_name}: {e}")
    
    except Exception as e:
        logger.error(f"Error in webhook notifications: {e}")
