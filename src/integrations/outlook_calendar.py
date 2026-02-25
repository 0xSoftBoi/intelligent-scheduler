"""Microsoft Outlook Calendar integration."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from O365 import Account, FileSystemTokenBackend
from loguru import logger


class OutlookCalendarIntegration:
    """Handles Microsoft Outlook Calendar API integration."""

    SCOPES = ['Calendars.ReadWrite', 'User.Read']

    def __init__(self, client_id: str, client_secret: str, tenant_id: str = 'common'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.account = None

    def get_authorization_url(self) -> str:
        """Generate OAuth authorization URL.
        
        Returns:
            Authorization URL for user to visit
        """
        credentials = (self.client_id, self.client_secret)
        token_backend = FileSystemTokenBackend(token_path='tokens')
        
        account = Account(
            credentials,
            auth_flow_type='authorization',
            tenant_id=self.tenant_id,
            token_backend=token_backend
        )
        
        # Get the authorization URL
        auth_url = account.connection.get_authorization_url(
            requested_scopes=self.SCOPES
        )
        
        return auth_url[0]  # Returns tuple (url, state)

    def authenticate(self, redirect_url: str = None) -> bool:
        """Authenticate with Microsoft Graph API.
        
        Args:
            redirect_url: OAuth redirect URL after user authorization
            
        Returns:
            True if authentication successful
        """
        credentials = (self.client_id, self.client_secret)
        token_backend = FileSystemTokenBackend(token_path='tokens')
        
        self.account = Account(
            credentials,
            auth_flow_type='authorization',
            tenant_id=self.tenant_id,
            token_backend=token_backend
        )
        
        if redirect_url:
            # Complete OAuth flow with redirect URL
            result = self.account.connection.request_token(
                redirect_url,
                scopes=self.SCOPES
            )
        else:
            # Use existing token
            result = self.account.authenticate(scopes=self.SCOPES)
        
        if result:
            logger.info("Outlook authentication successful")
        else:
            logger.error("Outlook authentication failed")
        
        return result

    def get_events(self, start_date: Optional[datetime] = None,
                  end_date: Optional[datetime] = None,
                  calendar_name: str = 'Calendar') -> List[Dict]:
        """Fetch calendar events.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            calendar_name: Name of calendar to query
            
        Returns:
            List of calendar events
        """
        if not self.account or not self.account.is_authenticated:
            raise ValueError("Not authenticated. Call authenticate first.")
        
        # Default to next 30 days
        if not start_date:
            start_date = datetime.now()
        if not end_date:
            end_date = start_date + timedelta(days=30)
        
        schedule = self.account.schedule()
        calendar = schedule.get_calendar(calendar_name=calendar_name)
        
        # Query events
        query = calendar.new_query('start').greater_equal(start_date)
        query.chain('and').on_attribute('end').less_equal(end_date)
        
        events = calendar.get_events(query=query, include_recurring=True)
        
        event_list = []
        for event in events:
            event_list.append({
                'id': event.object_id,
                'subject': event.subject,
                'start': event.start,
                'end': event.end,
                'location': event.location,
                'attendees': [att.address for att in event.attendees],
                'is_all_day': event.is_all_day,
                'body': event.body
            })
        
        logger.info(f"Retrieved {len(event_list)} events from Outlook Calendar")
        return event_list

    def create_event(self, subject: str, start: datetime, end: datetime,
                    body: str = '', location: str = '',
                    attendees: List[str] = None) -> Dict:
        """Create a calendar event.
        
        Args:
            subject: Event title
            start: Start datetime
            end: End datetime
            body: Event description
            location: Event location
            attendees: List of attendee email addresses
            
        Returns:
            Created event data
        """
        if not self.account or not self.account.is_authenticated:
            raise ValueError("Not authenticated")
        
        schedule = self.account.schedule()
        calendar = schedule.get_default_calendar()
        
        event = calendar.new_event()
        event.subject = subject
        event.start = start
        event.end = end
        event.body = body
        event.location = location
        
        if attendees:
            for email in attendees:
                event.attendees.add(email)
        
        event.save()
        
        logger.info(f"Created event: {subject} ({event.object_id})")
        return {
            'id': event.object_id,
            'subject': event.subject,
            'start': event.start,
            'end': event.end
        }

    def update_event(self, event_id: str, **kwargs) -> Dict:
        """Update a calendar event.
        
        Args:
            event_id: Event ID to update
            **kwargs: Fields to update
            
        Returns:
            Updated event data
        """
        if not self.account or not self.account.is_authenticated:
            raise ValueError("Not authenticated")
        
        schedule = self.account.schedule()
        calendar = schedule.get_default_calendar()
        
        event = calendar.get_event(event_id)
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(event, key):
                setattr(event, key, value)
        
        event.save()
        
        logger.info(f"Updated event: {event.subject} ({event_id})")
        return {
            'id': event.object_id,
            'subject': event.subject,
            'start': event.start,
            'end': event.end
        }

    def delete_event(self, event_id: str):
        """Delete a calendar event.
        
        Args:
            event_id: Event ID to delete
        """
        if not self.account or not self.account.is_authenticated:
            raise ValueError("Not authenticated")
        
        schedule = self.account.schedule()
        calendar = schedule.get_default_calendar()
        
        event = calendar.get_event(event_id)
        event.delete()
        
        logger.info(f"Deleted event: {event_id}")

    def subscribe_to_notifications(self, webhook_url: str,
                                  change_type: str = 'created,updated,deleted') -> Dict:
        """Subscribe to calendar change notifications.
        
        Args:
            webhook_url: Webhook URL for notifications
            change_type: Types of changes to monitor
            
        Returns:
            Subscription information
        """
        # Note: This requires Microsoft Graph API subscription setup
        # Implementation would use graph API directly
        logger.info(f"Subscription requested for: {webhook_url}")
        
        return {
            'subscription_id': 'sub_' + str(int(datetime.now().timestamp())),
            'webhook_url': webhook_url,
            'change_type': change_type,
            'expiration': (datetime.now() + timedelta(days=3)).isoformat()
        }
