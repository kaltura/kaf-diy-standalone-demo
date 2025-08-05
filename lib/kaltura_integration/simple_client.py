from KalturaClient import KalturaClient, KalturaConfiguration
from KalturaClient.Plugins.Core import KalturaSessionType
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Remove config import
# from config import config


class SimpleKalturaClient:
    """Simple Kaltura client wrapper using built-in session.start() method"""
    
    def __init__(self, partner_id: int, service_url: str):
        """
        Initialize the client with configuration
        Args:
            partner_id: Kaltura partner ID (required)
            service_url: Kaltura service URL (required)
        """
        self.partner_id = partner_id
        self.service_url = service_url
        self.client = None
    
    def _create_client(self) -> KalturaClient:
        """Create and configure Kaltura client"""
        client_config = KalturaConfiguration(self.partner_id)
        client_config.serviceUrl = self.service_url
        client_config.clientTag = "sample-cnc-app"
        return KalturaClient(client_config)
    
    def get_anonymous_client(self) -> KalturaClient:
        """
        Get an anonymous Kaltura client (no KS required)
        Returns:
            KalturaClient: Anonymous client instance
        """
        return self._create_client()
    
    def get_admin_client(self, admin_secret: str, user_id: str, expiry: int = 60) -> KalturaClient:
        """
        Get an admin Kaltura client using session.start()
        Args:
            admin_secret: Admin secret for the partner (required)
            user_id: Admin user ID (required)
            expiry: Session expiry time in seconds
        Returns:
            KalturaClient: Admin client instance with KS set
        """
        try:
            client = self._create_client()
            print(f"Creating admin session for partner {self.partner_id}, user {user_id}, expiry {expiry}")
            
            ks = client.session.start(
                admin_secret, 
                user_id, 
                KalturaSessionType.ADMIN, 
                self.partner_id, 
                expiry, 
                "disableentitlement"  
            )
            
            if not ks:
                raise Exception(f"Empty session token returned for partner {self.partner_id}")
                
            client.setKs(ks)
            print(f"Successfully created admin session for partner {self.partner_id}")
            return client
            
        except Exception as e:
            error_msg = str(e)
            print(f"Failed to create admin session for partner {self.partner_id}: {error_msg}")
            
            # Provide more specific error information
            if "START_SESSION_ERROR" in error_msg:
                raise Exception(f"Error while starting session for partner [{self.partner_id}] (START_SESSION_ERROR) - Please verify admin secret and user ID")
            elif "Invalid KS" in error_msg:
                raise Exception(f"Invalid session parameters for partner {self.partner_id} - Please check credentials")
            elif "partner" in error_msg.lower():
                raise Exception(f"Partner configuration error for partner {self.partner_id} - Please verify partner ID")
            else:
                raise Exception(f"Session creation failed for partner {self.partner_id}: {error_msg}")
    
    def get_user_client(self, admin_secret: str, user_id: str, privileges: str = "", expiry: int = 86400) -> KalturaClient:
        """
        Get a user Kaltura client using session.start()
        Args:
            admin_secret: Admin secret for the partner (required)
            user_id: User ID for the session (required)
            privileges: Privileges string (e.g., "edit,download")
            expiry: Session expiry time in seconds
        Returns:
            KalturaClient: User client instance with KS set
        """
        try:
            client = self._create_client()
            print(f"Creating user session for partner {self.partner_id}, user {user_id}, expiry {expiry}")
            
            ks = client.session.start(
                admin_secret, 
                user_id, 
                KalturaSessionType.USER, 
                self.partner_id, 
                expiry, 
                privileges
            )
            
            if not ks:
                raise Exception(f"Empty session token returned for partner {self.partner_id}")
                
            client.setKs(ks)
            print(f"Successfully created user session for partner {self.partner_id}")
            return client
            
        except Exception as e:
            error_msg = str(e)
            print(f"Failed to create user session for partner {self.partner_id}: {error_msg}")
            
            # Provide more specific error information
            if "START_SESSION_ERROR" in error_msg:
                raise Exception(f"Error while starting session for partner [{self.partner_id}] (START_SESSION_ERROR) - Please verify admin secret and user ID")
            elif "Invalid KS" in error_msg:
                raise Exception(f"Invalid session parameters for partner {self.partner_id} - Please check credentials")
            elif "partner" in error_msg.lower():
                raise Exception(f"Partner configuration error for partner {self.partner_id} - Please verify partner ID")
            else:
                raise Exception(f"Session creation failed for partner {self.partner_id}: {error_msg}")
    
    def get_client_with_custom_ks(self, admin_secret: str, user_id: str, session_type: int = KalturaSessionType.ADMIN, privileges: str = "", expiry: int = 86400) -> KalturaClient:
        """
        Get a Kaltura client with custom parameters using session.start()
        Args:
            admin_secret: Admin secret for the partner (required)
            user_id: User ID for the session (required)
            session_type: Session type (USER=0, ADMIN=2)
            privileges: Privileges string
            expiry: Session expiry time in seconds
        Returns:
            KalturaClient: Client instance with KS set
        """
        client = self._create_client()
        ks = client.session.start(
            admin_secret, 
            user_id, 
            session_type, 
            self.partner_id, 
            expiry, 
            privileges
        )
        client.setKs(ks)
        return client

# Convenience functions for backward compatibility
# All must require explicit credentials

def get_anonymous_client(partner_id: int, service_url: str) -> KalturaClient:
    """Get an anonymous Kaltura client"""
    return SimpleKalturaClient(partner_id, service_url).get_anonymous_client()


def get_admin_client(partner_id: int, service_url: str, admin_secret: str, user_id: str, expiry: int = 86400) -> KalturaClient:
    """Get an admin Kaltura client"""
    return SimpleKalturaClient(partner_id, service_url).get_admin_client(admin_secret, user_id, expiry)


def get_user_client(partner_id: int, service_url: str, admin_secret: str, user_id: str, privileges: str = "", expiry: int = 86400) -> KalturaClient:
    """Get a user Kaltura client"""
    return SimpleKalturaClient(partner_id, service_url).get_user_client(admin_secret, user_id, privileges, expiry)


def get_custom_client(partner_id: int, service_url: str, admin_secret: str, user_id: str, session_type: int = KalturaSessionType.ADMIN, privileges: str = "", expiry: int = 86400) -> KalturaClient:
    """Get a custom Kaltura client"""
    return SimpleKalturaClient(partner_id, service_url).get_client_with_custom_ks(admin_secret, user_id, session_type, privileges, expiry) 