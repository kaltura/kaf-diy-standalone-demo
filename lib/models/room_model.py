"""
KalturaRoomModel class handles operations related to Kaltura room creation.
Provides functionality for creating rooms and managing room configurations.
"""

import json
import requests
from typing import Optional, Dict, Any

from KalturaClient.Plugins.Room import KalturaRoomEntry

from .base_model import KalturaBaseModel


class KalturaRoomModel(KalturaBaseModel):
    """
    Kaltura Room Model for managing room creation and configuration.
    
    This class provides a comprehensive interface for:
    - Creating embedded rooms using the KAF API
    - Configuring room settings and associations
    - Managing room updates and broadcasts
    """
    
    def create_room_entry(
        self, 
        name: str, 
        description: Optional[str] = None,
        tags: Optional[str] = None, 
        live_entry_id_input: Optional[str] = None,
        template_room_entry_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an embedded room using the KAF API.
        
        This method creates a room using the KAF embedded rooms API endpoint
        and optionally associates it with a live stream entry.
        
        Args:
            name: The name of the room (mandatory)
            description: The description of the room (optional)
            tags: Comma-separated string of room tags (optional)
            live_entry_id_input: Live entry ID to associate with the room (optional)
            template_room_entry_id: Template room entry ID to use (optional)
            
        Returns:
            Dict[str, Any]: Created room response
            
        Raises:
            Exception: If room creation fails
        """
        # Append "_studio" to the room name
        room_name = f"{name}_studio"
        
        print("🚀 Starting createRoomEntry with parameters:", {
            'name': room_name,
            'description': description,
            'tags': tags,
            'liveEntryIdInput': live_entry_id_input,
            'templateRoomEntryId': template_room_entry_id
        })
        
        try:
            # Use the existing authenticated client for the KS
            ks = self.client.getKs()
            
            # Prepare request body
            request_body = self._build_room_request_body(
                ks, room_name, description, tags, template_room_entry_id
            )
            
            # Generate KAF instance URL and make request
            kaf_instance_url = f"https://{self.partner_id}.kaf.kaltura.com"
            create_room_url = f"{kaf_instance_url}/embeddedrooms/index/create-room"
            
            print(f"Creating room with URL: {create_room_url}")
            print(f"Request body: {request_body}")
            
            # Make the POST request
            response = requests.post(
                create_room_url,
                headers={'Content-Type': 'application/json'},
                json=request_body
            )
            
            if not response.ok:
                error_text = response.text
                raise Exception(f"Failed to create room: {response.status_code} {response.reason} - {error_text}")
            
            result = response.json()
            print(f"✅ Room created successfully: {result}")
            
            if not result.get('success'):
                raise Exception(f"Failed to create room: {result.get('message', 'Unknown error')}")
            
            # Log the structure for debugging
            print("Full result structure:", json.dumps(result, indent=2))
            print("Result data structure:", json.dumps(result.get('data', {}), indent=2))
            
            # Update room with broadcast entry ID if provided
            if live_entry_id_input and result.get('data'):
                print(f"🔄 Updating room with broadcast entry ID: {live_entry_id_input}")
                self._update_room_with_broadcast_entry(result, live_entry_id_input)
            else:
                print("ℹ️ No broadcast entry update performed")
            
            return result
            
        except Exception as error:
            print(f"❌ Error creating room: {error}")
            raise error
    
    def _build_room_request_body(
        self, 
        ks: str, 
        name: str, 
        description: Optional[str], 
        tags: Optional[str], 
        template_room_entry_id: Optional[str]
    ) -> Dict[str, Any]:
        """Build the request body for room creation."""
        request_body = {
            'ks': ks,
            'name': name
        }
        
        # Add optional parameters if provided
        if description:
            request_body['description'] = description
        if tags:
            request_body['tags'] = tags
        if template_room_entry_id and template_room_entry_id.strip() and template_room_entry_id != "null":
            request_body['templateRoomEntryId'] = template_room_entry_id
            
        return request_body
    
    def _update_room_with_broadcast_entry(self, result: Dict[str, Any], live_entry_id_input: str) -> None:
        """Update room with broadcast entry ID using Kaltura Room Service."""
        room_entry_id = result['data'].get('id')
        
        if room_entry_id:
            print(f"🔄 Updating room {room_entry_id} with broadcast entry ID: {live_entry_id_input}")
            
            try:
                # Create a KalturaRoomEntry object for the update
                room = KalturaRoomEntry()
                room.broadcastEntryId = live_entry_id_input
                
                # Update the room using the Kaltura Room Service
                update_result = self.client.room.room.update(room_entry_id, room)
                
                print("✅ Room update result:", {
                    'id': getattr(update_result, 'id', None),
                    'name': getattr(update_result, 'name', None),
                    'broadcastEntryId': getattr(update_result, 'broadcastEntryId', None)
                })
                
            except Exception as update_error:
                print(f"❌ Error updating room with broadcast entry: {update_error}")
                print("Error details:", {
                    'roomEntryId': room_entry_id,
                    'broadcastEntryId': live_entry_id_input,
                    'errorMessage': str(update_error)
                })
                # Don't throw the error as the room was created successfully
        else:
            print(f"⚠️ No room entry ID found in result.data: {result['data']}")
    
 