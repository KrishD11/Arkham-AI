"""Policy and authentication module for ACLED API OAuth"""

import logging
import requests
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from agent.config import Config

logger = logging.getLogger(__name__)


@dataclass
class ACLEDToken:
    """ACLED OAuth token"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 86400  # 24 hours in seconds
    expires_at: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.now() >= self.expires_at
    
    def is_expiring_soon(self, buffer_minutes: int = 60) -> bool:
        """Check if token is expiring soon"""
        buffer_time = timedelta(minutes=buffer_minutes)
        return datetime.now() >= (self.expires_at - buffer_time)


class ACLEDAuthPolicy:
    """Policy for ACLED API OAuth authentication"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize ACLED authentication policy"""
        self.config = config or Config()
        self.token_url = "https://acleddata.com/oauth/token"
        self.login_url = "https://acleddata.com/user/login?_format=json"
        self.api_base_url = "https://acleddata.com/api"
        self.client_id = "acled"
        self.token: Optional[ACLEDToken] = None
        self.session = requests.Session()  # Use session to maintain cookies
        
        # Get credentials from config
        self.username = self.config.ACLED_USERNAME
        # Handle URL-encoded passwords (Cloud Run may URL-encode special chars)
        import urllib.parse
        self.password = urllib.parse.unquote(self.config.ACLED_PASSWORD) if self.config.ACLED_PASSWORD else None
    
    def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """Get a valid access token"""
        # Check if we have a valid token
        if self.token and not self.token.is_expired() and not force_refresh:
            return self.token.access_token
        
        # Check if we can refresh
        if self.token and self.token.refresh_token and not force_refresh:
            try:
                if self._refresh_token():
                    return self.token.access_token
            except Exception as e:
                logger.warning(f"Failed to refresh token: {e}. Requesting new token.")
        
        # Request new token
        try:
            self._request_new_token()
            return self.token.access_token if self.token else None
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            return None
    
    def _request_new_token(self) -> None:
        """Request a new access token using username and password"""
        if not self.username or not self.password:
            raise ValueError("ACLED username and password must be configured")
        
        # Try OAuth token endpoint first (standard method)
        try:
            # Use data parameter (not json) to send form-urlencoded data
            # requests will automatically set Content-Type and encode the data
            data = {
                'username': self.username,
                'password': self.password,
                'grant_type': 'password',
                'client_id': self.client_id
            }
            
            # Don't set Content-Type header - let requests handle it
            # Use session to maintain cookies if login was called
            response = self.session.post(self.token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Calculate expiration time
                expires_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 86400))
                
                self.token = ACLEDToken(
                    access_token=token_data['access_token'],
                    refresh_token=token_data['refresh_token'],
                    token_type=token_data.get('token_type', 'Bearer'),
                    expires_in=token_data.get('expires_in', 86400),
                    expires_at=expires_at
                )
                
                logger.info(f"Successfully obtained ACLED access token via OAuth. Expires at {expires_at}")
                return
        except Exception as e:
            logger.warning(f"OAuth token request failed: {e}. Trying alternative login method.")
        
        # Fallback: Try user/login endpoint first, then OAuth token
        # Sometimes login is needed before OAuth token request works
        try:
            login_data = {
                "name": self.username,
                "pass": self.password
            }
            
            login_response = self.session.post(
                self.login_url, 
                json=login_data, 
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                csrf_token = login_result.get('csrf_token')
                logger.info(f"Successfully logged in via user/login endpoint. CSRF token obtained.")
                
                # Now try OAuth token request with session cookies
                data = {
                    'username': self.username,
                    'password': self.password,
                    'grant_type': 'password',
                    'client_id': self.client_id
                }
                
                oauth_response = self.session.post(self.token_url, data=data)
                
                if oauth_response.status_code == 200:
                    token_data = oauth_response.json()
                    expires_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 86400))
                    
                    self.token = ACLEDToken(
                        access_token=token_data['access_token'],
                        refresh_token=token_data['refresh_token'],
                        token_type=token_data.get('token_type', 'Bearer'),
                        expires_in=token_data.get('expires_in', 86400),
                        expires_at=expires_at
                    )
                    
                    logger.info(f"Successfully obtained ACLED access token after login. Expires at {expires_at}")
                    return
                else:
                    raise Exception(f"OAuth token request failed after login: {oauth_response.status_code}")
        except Exception as e:
            logger.error(f"Login + OAuth method failed: {e}")
        
        # If all methods fail, raise error
        error_msg = response.text[:500] if 'response' in locals() and response.text else "No error message"
        raise Exception(
            f"Failed to get access token: {error_msg}"
        )
    
    def _refresh_token(self) -> bool:
        """Refresh access token using refresh token"""
        if not self.token or not self.token.refresh_token:
            return False
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        data = {
            'refresh_token': self.token.refresh_token,
            'grant_type': 'refresh_token',
            'client_id': self.client_id
        }
        
        try:
            response = self.session.post(self.token_url, headers=headers, data=data)
            
            if response.status_code != 200:
                logger.warning(f"Token refresh failed: {response.status_code}")
                return False
            
            token_data = response.json()
            
            # Calculate expiration time
            expires_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 86400))
            
            self.token = ACLEDToken(
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                token_type=token_data.get('token_type', 'Bearer'),
                expires_in=token_data.get('expires_in', 86400),
                expires_at=expires_at
            )
            
            logger.info(f"Successfully refreshed ACLED access token. Expires at {expires_at}")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return False
    
    def get_authorization_header(self) -> Dict[str, str]:
        """Get authorization header for API requests"""
        token = self.get_access_token()
        if not token:
            raise Exception("Unable to obtain access token")
        
        return {"Authorization": f"Bearer {token}"}
    
    def make_authenticated_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """Make an authenticated request to ACLED API"""
        # Get authorization header
        auth_headers = self.get_authorization_header()
        
        # Merge with custom headers
        request_headers = {
            "Content-Type": "application/json",
            **auth_headers
        }
        if headers:
            request_headers.update(headers)
        
        # Build URL
        url = f"{self.api_base_url}/{endpoint}"
        
        # Make request
        if method.upper() == "GET":
            response = self.session.get(url, headers=request_headers, params=params)
        elif method.upper() == "POST":
            response = self.session.post(url, headers=request_headers, json=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Handle token expiration
        if response.status_code == 401:
            logger.warning("Token expired, refreshing...")
            self.get_access_token(force_refresh=True)
            # Retry request
            auth_headers = self.get_authorization_header()
            request_headers.update(auth_headers)
            if method.upper() == "GET":
                response = self.session.get(url, headers=request_headers, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=request_headers, json=params)
        
        return response
    
    def fetch_acled_data(
        self,
        endpoint: str = "acled/read",
        country: Optional[str] = None,
        year: Optional[int] = None,
        event_date: Optional[str] = None,
        event_date_where: Optional[str] = None,
        fields: Optional[str] = None,
        limit: Optional[int] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Fetch data from ACLED API"""
        params = {
            "_format": format
        }
        
        if country:
            params["country"] = country
        if year:
            params["year"] = year
        if event_date:
            params["event_date"] = event_date
        if event_date_where:
            params["event_date_where"] = event_date_where
        if fields:
            params["fields"] = fields
        if limit:
            params["limit"] = limit
        
        response = self.make_authenticated_request(endpoint, params=params)
        
        if response.status_code != 200:
            raise Exception(
                f"ACLED API request failed: {response.status_code} {response.text}"
            )
        
        return response.json()


# Global policy instance
_policy_instance: Optional[ACLEDAuthPolicy] = None


def get_acled_auth_policy() -> ACLEDAuthPolicy:
    """Get or create the global ACLED authentication policy instance"""
    global _policy_instance
    if _policy_instance is None:
        _policy_instance = ACLEDAuthPolicy()
    return _policy_instance

