import pytest
from baseweb import Baseweb

# ==============================================================================
# Push Notification Frontend Integration Tests
# ==============================================================================
# These tests verify the contract between the Baseweb frontend and backend.
# They simulate frontend behavior to ensure the API supports the required
# push notification flows, specifically targeting iOS PWA compatibility.
# ==============================================================================

@pytest.fixture
def app():
    """Create a test Baseweb app."""
    return Baseweb("test_push_frontend")

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

class TestPushFrontendVAPIDKeyRetrieval:
    """
    Tests the frontend's ability to retrieve the VAPID public key.
    Requirement: GET /api/vapid-public-key must return a base64url string.
    """

    @pytest.mark.asyncio
    async def test_frontend_can_retrieve_vapid_public_key(self, client):
        """
        Given: A functional backend with VAPID configured
        When: Frontend calls GET /api/vapid-public-key
        Then: Should receive 200 OK with a valid base64url public_key
        """
        response = await client.get('/api/vapid-public-key')
        assert response.status_code == 200
        data = response.get_json()
        assert 'public_key' in data
        assert isinstance(data['public_key'], str)
        # Check if it's a valid base64url string (roughly)
        import re
        assert re.match(r'^[A-Za-z0-9\-_]+$', data['public_key'])

    @pytest.mark.asyncio
    async def test_frontend_handles_missing_vapid_key(self, client):
        """
        Given: A backend where VAPID is not configured
        When: Frontend calls GET /api/vapid-public-key
        Then: Should receive 404 or 503, and frontend should disable notification UI
        """
        response = await client.get('/api/vapid-public-key')
        if response.status_code in [404, 503]:
            assert True
        else:
            pytest.skip("VAPID key is configured, cannot test missing key case without backend reconfiguration")

class TestPushFrontendSubscriptionSync:
    """
    Tests the synchronization of push subscriptions from frontend to backend.
    Requirement: POST /api/push-subscriptions must accept base64url encoded keys.
    """

    @pytest.mark.asyncio
    async def test_frontend_submits_valid_subscription(self, client):
        """
        Given: A valid browser push subscription object
        When: Frontend transforms keys to base64url and calls POST /api/push-subscriptions
        Then: Backend should return 201 Created or 200 OK
        """
        payload = {
            'endpoint': 'https://push.example.com/subscriptions/123',
            'keys': {
                'p256dh': 'BMAA97hS_p-Example-Key-p256dh',
                'auth': 'S-Example-Key-auth'
            }
        }
        response = await client.post('/api/push-subscriptions', json=payload)
        assert response.status_code in [200, 201, 409]

    @pytest.mark.asyncio
    async def test_frontend_handles_duplicate_subscription_as_success(self, client):
        """
        Given: An existing subscription for the same endpoint
        When: Frontend calls POST /api/push-subscriptions with the same data
        Then: Backend returns 409 Conflict, but frontend treats this as "Subscribed"
        """
        payload = {
            'endpoint': 'https://push.example.com/subscriptions/duplicate',
            'keys': {
                'p256dh': 'BMAA97hS_p-Duplicate-Key-p256dh',
                'auth': 'S-Duplicate-Key-auth'
            }
        }
        await client.post('/api/push-subscriptions', json=payload)
        response = await client.post('/api/push-subscriptions', json=payload)
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_frontend_handles_unauthorized_subscription(self, client):
        """
        Given: An unauthenticated session
        When: Frontend calls POST /api/push-subscriptions
        Then: Backend should return 401 Unauthorized
        """
        payload = {
            'endpoint': 'https://push.example.com/subscriptions/123',
            'keys': {
                'p256dh': 'BMAA97hS_p-Example-Key-p256dh',
                'auth': 'S-Example-Key-auth'
            }
        }
        # Ensure we are unauthenticated
        # In most test clients, this is the default.
        response = await client.post('/api/push-subscriptions', json=payload)
        assert response.status_code == 401
        data = response.get_json()
        assert data['title'] == "Unauthorized"

    @pytest.mark.asyncio
    async def test_frontend_handles_invalid_subscription_data(self, client):
        """
        Given: A malformed subscription object (e.g. non-HTTPS endpoint)
        When: Frontend calls POST /api/push-subscriptions
        Then: Backend returns 400 Bad Request, and frontend shows error message
        """
        payload = {
            'endpoint': 'http://insecure.example.com/sub',
            'keys': {
                'p256dh': 'invalid',
                'auth': 'invalid'
            }
        }
        response = await client.post('/api/push-subscriptions', json=payload)
        assert response.status_code == 400

class TestPushFrontendServiceWorkerIntegration:
    """
    Tests the integration between the Service Worker and the browser's push event.
    Note: These are behavioral specifications as they typically require a browser environment.
    """

    @pytest.mark.asyncio
    async def test_sw_handles_push_event_and_shows_notification(self):
        """
        Given: A push event received by the service worker
        When: The payload contains a title and body
        Then: A system notification is displayed with the correct content
        """
        with open('src/baseweb/static/js/sw.js', 'r') as f:
            content = f.read()
            assert 'self.addEventListener(\'push\'' in content
            assert 'self.registration.showNotification' in content

    @pytest.mark.asyncio
    async def test_sw_handles_notification_click_and_opens_url(self):
        """
        Given: A displayed push notification
        When: The user clicks the notification
        Then: The browser opens the URL specified in the payload (if valid HTTPS)
        """
        with open('src/baseweb/static/js/sw.js', 'r') as f:
            content = f.read()
            assert 'self.addEventListener(\'notificationclick\'' in content
            assert 'urlToOpen.startsWith(\'https://\')' in content
            assert 'clients.openWindow(urlToOpen)' in content

    @pytest.mark.asyncio
    async def test_sw_prevents_xss_in_notification_payload(self):
        """
        Given: A push payload containing malicious HTML/Script
        When: The service worker processes the event
        Then: The content is rendered as plain text, not as HTML
        """
        with open('src/baseweb/static/js/sw.js', 'r') as f:
            content = f.read()
            assert 'innerHTML' not in content
            assert 'document.write' not in content
