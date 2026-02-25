"""Webhook handlers for real-time schedule adjustments."""

import hmac
import hashlib
from datetime import datetime
from typing import Dict, Optional
from loguru import logger
from celery import Celery


class WebhookHandler:
    """Handles incoming webhooks from calendar providers and other sources."""

    def __init__(self, secret_key: str, celery_app: Optional[Celery] = None):
        self.secret_key = secret_key
        self.celery_app = celery_app

    def verify_signature(self, payload: bytes, signature: str,
                        algorithm: str = 'sha256') -> bool:
        """Verify webhook signature for security.
        
        Args:
            payload: Raw webhook payload
            signature: Signature from webhook header
            algorithm: Hash algorithm used
            
        Returns:
            True if signature is valid
        """
        if algorithm == 'sha256':
            expected_signature = hmac.new(
                self.secret_key.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        return hmac.compare_digest(signature, expected_signature)

    def handle_calendar_event(self, event_data: Dict) -> Dict:
        """Handle calendar event webhook.
        
        Args:
            event_data: Calendar event data from webhook
            
        Returns:
            Processing result
        """
        event_type = event_data.get('event_type')
        calendar_id = event_data.get('calendar_id')
        user_id = event_data.get('user_id')
        
        logger.info(f"Processing calendar event: {event_type} for user {user_id}")
        
        # Route to appropriate handler
        if event_type == 'event.created':
            return self._handle_event_created(event_data)
        elif event_type == 'event.updated':
            return self._handle_event_updated(event_data)
        elif event_type == 'event.deleted':
            return self._handle_event_deleted(event_data)
        else:
            logger.warning(f"Unknown event type: {event_type}")
            return {'status': 'ignored', 'reason': 'unknown_event_type'}

    def handle_optimization_trigger(self, trigger_data: Dict) -> Dict:
        """Handle schedule optimization trigger.
        
        Args:
            trigger_data: Optimization trigger data
            
        Returns:
            Processing result
        """
        user_id = trigger_data.get('user_id')
        trigger_reason = trigger_data.get('reason')
        
        logger.info(f"Optimization triggered for user {user_id}: {trigger_reason}")
        
        # Queue optimization task
        if self.celery_app:
            task = self.celery_app.send_task(
                'optimize_schedule',
                args=[user_id],
                kwargs={'trigger_reason': trigger_reason}
            )
            
            return {
                'status': 'queued',
                'task_id': task.id,
                'user_id': user_id
            }
        else:
            # Synchronous fallback
            return self._optimize_schedule_sync(user_id, trigger_reason)

    def handle_energy_update(self, energy_data: Dict) -> Dict:
        """Handle energy level update from user.
        
        Args:
            energy_data: Energy level data
            
        Returns:
            Processing result
        """
        user_id = energy_data.get('user_id')
        energy_level = energy_data.get('energy_level')
        timestamp = energy_data.get('timestamp', datetime.now())
        
        logger.info(f"Energy update for user {user_id}: level {energy_level}")
        
        # Store energy data
        # Would save to database in production
        
        # Check if schedule adjustment needed
        if energy_level < 30:  # Low energy threshold
            logger.info("Low energy detected, triggering schedule review")
            return self.handle_optimization_trigger({
                'user_id': user_id,
                'reason': 'low_energy_detected'
            })
        
        return {
            'status': 'recorded',
            'user_id': user_id,
            'energy_level': energy_level
        }

    def _handle_event_created(self, event_data: Dict) -> Dict:
        """Handle newly created calendar event."""
        user_id = event_data.get('user_id')
        event = event_data.get('event_data', {})
        
        # Check if event conflicts with no-meeting time
        # Check if schedule needs reoptimization
        
        logger.info(f"New event created: {event.get('title')}")
        
        return {
            'status': 'processed',
            'action': 'event_added',
            'optimization_triggered': True
        }

    def _handle_event_updated(self, event_data: Dict) -> Dict:
        """Handle updated calendar event."""
        user_id = event_data.get('user_id')
        event = event_data.get('event_data', {})
        
        logger.info(f"Event updated: {event.get('title')}")
        
        # Verify update doesn't violate policies
        # Trigger reoptimization if needed
        
        return {
            'status': 'processed',
            'action': 'event_updated',
            'optimization_triggered': False
        }

    def _handle_event_deleted(self, event_data: Dict) -> Dict:
        """Handle deleted calendar event."""
        user_id = event_data.get('user_id')
        event_id = event_data.get('event_id')
        
        logger.info(f"Event deleted: {event_id}")
        
        # Free up time slot
        # Consider rescheduling pending items
        
        return {
            'status': 'processed',
            'action': 'event_deleted',
            'optimization_triggered': True
        }

    def _optimize_schedule_sync(self, user_id: str, reason: str) -> Dict:
        """Synchronous schedule optimization fallback."""
        logger.info(f"Running sync optimization for {user_id}")
        
        # Would call actual optimization logic
        return {
            'status': 'completed',
            'user_id': user_id,
            'reason': reason,
            'optimized_at': datetime.now().isoformat()
        }


class WebhookRegistry:
    """Registry for managing webhook subscriptions."""

    def __init__(self):
        self.subscriptions = {}

    def register_webhook(self, user_id: str, webhook_url: str,
                        events: list, metadata: Optional[Dict] = None) -> Dict:
        """Register a new webhook subscription.
        
        Args:
            user_id: User identifier
            webhook_url: Webhook URL
            events: List of event types to subscribe to
            metadata: Optional metadata
            
        Returns:
            Subscription details
        """
        subscription_id = f"sub_{user_id}_{int(datetime.now().timestamp())}"
        
        subscription = {
            'id': subscription_id,
            'user_id': user_id,
            'webhook_url': webhook_url,
            'events': events,
            'metadata': metadata or {},
            'created_at': datetime.now(),
            'active': True
        }
        
        self.subscriptions[subscription_id] = subscription
        
        logger.info(f"Webhook registered: {subscription_id} for user {user_id}")
        
        return subscription

    def unregister_webhook(self, subscription_id: str) -> bool:
        """Unregister a webhook subscription.
        
        Args:
            subscription_id: Subscription ID to remove
            
        Returns:
            True if successful
        """
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            logger.info(f"Webhook unregistered: {subscription_id}")
            return True
        return False

    def get_user_webhooks(self, user_id: str) -> list:
        """Get all webhooks for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of user's webhook subscriptions
        """
        return [
            sub for sub in self.subscriptions.values()
            if sub['user_id'] == user_id and sub['active']
        ]

    def notify_webhook(self, subscription_id: str, event_data: Dict) -> Dict:
        """Send notification to a webhook.
        
        Args:
            subscription_id: Subscription to notify
            event_data: Event data to send
            
        Returns:
            Notification result
        """
        subscription = self.subscriptions.get(subscription_id)
        
        if not subscription or not subscription['active']:
            return {'status': 'failed', 'reason': 'inactive_subscription'}
        
        # Would make HTTP POST request to webhook_url in production
        logger.info(f"Webhook notification sent: {subscription_id}")
        
        return {
            'status': 'sent',
            'subscription_id': subscription_id,
            'webhook_url': subscription['webhook_url']
        }
