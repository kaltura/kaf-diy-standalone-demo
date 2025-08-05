"""
KalturaLiveEventModel class handles operations related to Kaltura live stream events.
Provides functionality for creating live sessions, adding metadata, and retrieving session details.
"""

import json
import requests
from typing import Optional, Dict, Any

from KalturaClient.Plugins.Core import (
    KalturaLiveStreamEntry, KalturaMediaType,
    KalturaDVRStatus, KalturaEntryStatus, KalturaSourceType,
    KalturaNullableBoolean, KalturaLiveEntryRecordingOptions,
    KalturaBaseEntry, KalturaCategoryEntry
)
from KalturaClient.Plugins.Metadata import KalturaMetadataObjectType

from .base_model import KalturaBaseModel


class KalturaLiveEventModel(KalturaBaseModel):
    """
    Kaltura Live Event Model for managing live stream sessions.
    
    This class provides a comprehensive interface for:
    - Creating and managing live stream entries
    - Adding metadata and managing entry relationships
    - Retrieving session details
    """
    

    
    def create_live_entry(
        self, 
        event_name: str, 
        event_description: str,
        user_id: Optional[str] = None, 
        category_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Kwebcast live stream entry with the specified name and description.
        The entry will be marked as a Kwebcast entry with appropriate metadata.
        
        Args:
            event_name: The name of the live event
            event_description: The description of the live event
            user_id: The user ID for the entry (optional, defaults to admin user)
            category_id: The category ID to add the entry to (optional)
            
        Returns:
            Dict[str, Any]: Live stream response
            
        Raises:
            Exception: If the live stream creation fails
        """
        try:
            entry_user_id = user_id or self.user_id or ""
            
            # Configure live stream entry
            live_stream_entry = KalturaLiveStreamEntry()
            live_stream_entry.name = event_name
            live_stream_entry.description = event_description
            live_stream_entry.adminTags = "kms-webcast-event,kwebcast"  # Mark as Kwebcast entry
            live_stream_entry.dvrStatus = KalturaDVRStatus.ENABLED
            live_stream_entry.dvrWindow = 1440
            live_stream_entry.mediaType = KalturaMediaType.LIVE_STREAM_FLASH
            live_stream_entry.recordStatus = 1
            live_stream_entry.explicitLive = KalturaNullableBoolean.TRUE_VALUE
            live_stream_entry.entitledUsersEdit = "WebcastingAdmin"
            
            # Configure recording options
            recording_options = KalturaLiveEntryRecordingOptions()
            recording_options.shouldCopyEntitlement = KalturaNullableBoolean.FALSE_VALUE
            recording_options.shouldMakeHidden = KalturaNullableBoolean.FALSE_VALUE
            live_stream_entry.recordingOptions = recording_options
            
            # Create the live stream entry
            live_stream_response = self.client.liveStream.add(live_stream_entry, KalturaSourceType.LIVE_STREAM)
            
            # Add Kwebcast metadata and category if specified
            if live_stream_response and hasattr(live_stream_response, 'id'):
                print("🏷️ Adding Kwebcast metadata...")
                self.add_kwebcast_metadata(live_stream_response.id)
                
                if category_id and category_id.strip():
                    print(f"🏷️ Category ID provided: '{category_id}', adding entry to category...")
                    self.add_entry_to_category(live_stream_response.id, category_id)
                else:
                    print(f"⚠️ No category ID provided or empty. Entry will not be added to any category.")
            
            print(f"✅ Kwebcast live session created successfully: {live_stream_response.id}")
            return live_stream_response
            
        except Exception as error:
            print(f"❌ Error creating Kwebcast live session: {error}")
            raise error
    
    def add_kwebcast_metadata(self, entry_id: str) -> Optional[Any]:
        """
        Add Kwebcast metadata to an existing entry.
        
        This method searches for the KwebcastProfile metadata profile and adds
        the appropriate XML metadata to mark the entry as a Kwebcast entry.
        
        Args:
            entry_id: The ID of the entry to add metadata to
            
        Returns:
            Optional[Any]: Metadata response if successful, None if failed
            
        Raises:
            Exception: If metadata addition fails
        """
        try:
            # Search for KwebcastProfile metadata profile
            print("🔍 Searching for KwebcastProfile metadata profile...")
            profiles_list = self.client.metadata.metadataProfile.list()
            
            kwebcast_profile_id = None
            if profiles_list and hasattr(profiles_list, 'objects') and profiles_list.objects:
                for profile in profiles_list.objects:
                    if hasattr(profile, 'name') and profile.name == "KwebcastProfile":
                        kwebcast_profile_id = profile.id
                        print(f"✅ Found KwebcastProfile with ID: {kwebcast_profile_id}")
                        break
            
            if kwebcast_profile_id:
                # Create the metadata XML for KwebcastProfile
                metadata_xml = """<metadata>
  <SlidesDocEntryId></SlidesDocEntryId>
  <IsKwebcastEntry>1</IsKwebcastEntry>
  <IsSelfServe>0</IsSelfServe>
</metadata>"""
                
                # Add metadata to the entry
                metadata_response = self.client.metadata.metadata.add(
                    metadataProfileId=kwebcast_profile_id,
                    objectType=KalturaMetadataObjectType.ENTRY,
                    objectId=entry_id,
                    xmlData=metadata_xml
                )
                
                print(f"✅ Kwebcast metadata added successfully to live entry {entry_id}")
                return metadata_response
            else:
                print("⚠️  Warning: KwebcastProfile not found. Entry created without Kwebcast metadata.")
                self._log_available_profiles(profiles_list)
                return None
                
        except Exception as metadata_error:
            print(f"⚠️  Warning: Failed to add Kwebcast metadata: {metadata_error}")
            return None
    
    def _log_available_profiles(self, profiles_list) -> None:
        """Log available metadata profiles for debugging."""
        print("Available profiles:")
        if profiles_list and hasattr(profiles_list, 'objects') and profiles_list.objects:
            for profile in profiles_list.objects:
                print(f"  - ID: {profile.id}, Name: '{profile.name}', SystemName: '{profile.systemName}'")
    
    def add_entry_to_category(self, entry_id: str, category_id: str) -> Optional[Any]:
        """
        Add an entry to a category.
        
        Args:
            entry_id: The ID of the entry to add to the category
            category_id: The ID of the category to add the entry to
            
        Returns:
            Optional[Any]: Category entry response if successful, None if failed
            
        Raises:
            Exception: If adding entry to category fails
        """
        try:
            print(f"🏷️ Adding entry {entry_id} to category {category_id}...")
            
            # Create category entry object
            category_entry = KalturaCategoryEntry()
            category_entry.entryId = entry_id
            category_entry.categoryId = int(category_id)
            
            # Add entry to category
            result = self.client.categoryEntry.add(category_entry)
            
            print(f"✅ Entry '{entry_id}' published to Category '{category_id}' successfully.")
            return result
            
        except Exception as error:
            print(f"❌ Error adding entry to category: {error}")
            raise error 