"""
Base model class for Kaltura models with common initialization logic.
"""

from typing import Dict, Any
from ..kaltura_integration.simple_client import get_admin_client


class KalturaBaseModel:
    """
    Base model class for Kaltura operations.
    
    This class provides common initialization and client setup
    that can be shared across different Kaltura model types.
    """
    
    def __init__(self, partner_id: int, service_url: str, admin_secret: str, user_id: str):
        """
        Initialize the base model with admin client.
        
        Args:
            partner_id: Kaltura partner ID
            service_url: Kaltura service URL
            admin_secret: Admin secret for authentication
            user_id: User ID for operations
        """
        self.partner_id = partner_id
        self.service_url = service_url
        self.admin_secret = admin_secret
        self.user_id = user_id
        self.client = get_admin_client(partner_id, service_url, admin_secret, user_id)
    
    def get_session(self, entry_id: str):
        """
        Retrieve a session entry by its ID using the BaseEntry service.
        
        Args:
            entry_id: The unique identifier of the session/entry to retrieve
            
        Returns:
            Dict[str, Any]: Session/entry details as a dictionary
            
        Raises:
            Exception: If the retrieval request fails
        """
        try:
            result = self.client.baseEntry.get(entry_id)
            print(f"✅ Entry retrieved successfully: {result}")
            
            # Convert to dictionary with consistent structure
            session_data = {
                'id': getattr(result, 'id', None),
                'name': getattr(result, 'name', None),
                'description': getattr(result, 'description', None),
                'status': str(getattr(result, 'status', None)) if getattr(result, 'status', None) is not None else None,
                'tags': getattr(result, 'tags', None),
                'createdAt': getattr(result, 'createdAt', None),
                'updatedAt': getattr(result, 'updatedAt', None),
                'type': str(getattr(result, 'type', None)) if getattr(result, 'type', None) is not None else None
            }
            
            return session_data
            
        except Exception as error:
            print(f"❌ Error retrieving entry by ID: {error}")
            raise error 