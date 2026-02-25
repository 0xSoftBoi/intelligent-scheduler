"""Google Calendar integration."""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from loguru import logger


class GoogleCalendarIntegration:
    """Handles Google Calendar API integration."""

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self, credentials_file: str = 'config/google_credentials.json'):
        self.credentials_file = credentials_file
        self.service = None

    def get_authorization_url(self, redirect_uri: str) -> str:
        """Generate OAuth authorization URL.
        
        Args:
            redirect_uri: OAuth redirect URI
            
        Returns:
            Authorization URL for user to visit
        """
        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return auth_url

    def exchange_code_for_token(self, auth_code: str, redirect_uri: str) -> Dict:
        """Exchange authorization code for access token.
        
        Args:
            auth_code: Authorization code from OAuth flow
            redirect_uri: OAuth redirect URI
            
        Returns:
            Token information
        """
        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

    def initialize_service(self, token_data: Dict):
        """Initialize Google Calendar service with credentials.
        
        Args:
            token_data: OAuth token data
        """
        credentials = Credentials(
            token=token_data['token'],
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
        )
        
        self.service = build('calendar', 'v3', credentials=credentials)
        logger.info("Google Calendar service initialized")

    def get_events(self, calendar_id: str = 'primary',
                  start_date: Optional[datetime] = None,
                  end_date: Optional[datetime] = None,
                  max_results: int = 100) -> List[Dict]:
        """Fetch calendar events.
        
        Args:
            calendar_id: Calendar ID (default: primary)
            start_date: Start of date range
            end_date: End of date range
            max_results: Maximum events to retrieve
            
        Returns:
            List of calendar events
        """
        if not self.service:
            raise ValueError("Service not initialized. Call initialize_service first.")
        
        # Default to next 30 days
        if not start_date:
            start_date = datetime.now()
        if not end_date:
            end_date = start_date + timedelta(days=30)
        
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        logger.info(f"Retrieved {len(events)} events from Google Calendar")
        
        return events

    def create_event(self, calendar_id: str, event_data: Dict) -> Dict:
        """Create a calendar event.
        
        Args:
            calendar_id: Calendar ID
            event_data: Event details
            
        Returns:
            Created event data
        """
        if not self.service:
            raise ValueError("Service not initialized")
        
        event = self.service.events().insert(
            calendarId=calendar_id,
            body=event_data
        ).execute()
        
        logger.info(f"Created event: {event.get('summary')} ({event.get('id')})")
        return event

    def update_event(self, calendar_id: str, event_id: str,
                    event_data: Dict) -> Dict:
        """Update a calendar event.
        
        Args:
            calendar_id: Calendar ID
            event_id: Event ID to update
            event_data: Updated event details
            
        Returns:
            Updated event data
        """
        if not self.service:
            raise ValueError("Service not initialized")
        
        event = self.service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_data
        ).execute()
        
        logger.info(f"Updated event: {event.get('summary')} ({event_id})")
        return event

    def delete_event(self, calendar_id: str, event_id: str):
        """Delete a calendar event.
        
        Args:
            calendar_id: Calendar ID
            event_id: Event ID to delete
        """
        if not self.service:
            raise ValueError("Service not initialized")
        
        self.service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        logger.info(f"Deleted event: {event_id}")

    def watch_calendar(self, calendar_id: str, webhook_url: str,
                      channel_id: str) -> Dict:
        """Set up calendar watch for real-time updates.
        
        Args:
            calendar_id: Calendar ID to watch
            webhook_url: Webhook URL for notifications
            channel_id: Unique channel identifier
            
        Returns:
            Watch channel information
        """
        if not self.service:
            raise ValueError("Service not initialized")
        
        body = {
            'id': channel_id,
            'type': 'web_hook',
            'address': webhook_url
        }
        
        channel = self.service.events().watch(
            calendarId=calendar_id,
            body=body
        ).execute()
        
        logger.info(f"Calendar watch established: {channel_id}")
        return channel

    def stop_watch(self, channel_id: str, resource_id: str):
        """Stop calendar watch.
        
        Args:
            channel_id: Channel ID
            resource_id: Resource ID from watch response
        """
        if not self.service:
            raise ValueError("Service not initialized")
        
        body = {
            'id': channel_id,
            'resourceId': resource_id
        }
        
        self.service.channels().stop(body=body).execute()
        logger.info(f"Calendar watch stopped: {channel_id}")
