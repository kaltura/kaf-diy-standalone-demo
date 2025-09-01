"""
KalturaSubTenantModel class handles operations related to Kaltura sub-tenant management.
Provides functionality for creating sub-tenants, managing categories, and partner operations.
"""

import time
import os
import requests
import logging
from typing import Optional, Dict, Any

from KalturaClient.Plugins.Core import (
    KalturaPartner, KalturaPartnerType, KalturaKeyValue, 
    KalturaCategory, KalturaCategoryFilter, KalturaFilterPager
)

from ..kaltura_integration.simple_client import get_admin_client


class KalturaSubTenantModel:
    """
    Kaltura Sub-Tenant Model for managing sub-tenants and categories.
    
    This class provides a comprehensive interface for:
    - Creating and managing sub-tenants
    - Managing categories and publishing channels
    - Partner configuration and module management
    """
    
    # Configuration constants
    DEFAULT_PAGE_SIZE = 500
    DEFAULT_PAGE_INDEX = 1
    DEFAULT_SEARCH_ATTEMPTS = 3
    DEFAULT_SEARCH_WAIT_TIME = 10  # seconds
    
    def __init__(self, partner_id: int, service_url: str, admin_secret: str, user_id: str):
        """
        Initialize the sub-tenant model with admin client.
        
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
        
        # Initialize logger for this instance
        self.logger = logging.getLogger(__name__)
    
    def create_sub_tenant(
        self, 
        partner_name: str, 
        partner_email: str,
        template_partner_id: int, 
        partner_description: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new Kaltura sub-tenant.
        
        Args:
            partner_name: Name of the new partner
            partner_email: Email for the partner admin
            template_partner_id: Template partner ID to use
            partner_description: Description for the partner (optional)
            
        Returns:
            Dict[str, Any]: Created partner information
            
        Raises:
            Exception: If sub-tenant creation fails
        """
        try:
            partner = self._build_partner_object(partner_name, partner_email, partner_description)
            
            # Register the partner
            cms_password = ""
            silent = False
            result = self.client.partner.register(partner, cms_password, template_partner_id, silent)
            
            if not result:
                raise Exception('Failed to create sub-tenant: null response')
            
            response_data = {
                'id': getattr(result, 'id', None),
                'templatePartnerId': getattr(result, 'templatePartnerId', None),
                'partnerPackage': getattr(result, 'partnerPackage', None),
                'referenceId': getattr(result, 'referenceId', None),
                'email': getattr(result, 'adminEmail', None),
                'adminSecret': getattr(result, 'adminSecret', None),
                'adminUserId': getattr(result, 'adminUserId', None)
            }
            
            print(f"✅ Sub-tenant created successfully: {response_data['id']}")
            return response_data
            
        except Exception as error:
            print(f"❌ Error creating sub-tenant: {error}")
            raise error
    
    def _build_partner_object(self, partner_name: str, partner_email: str, partner_description: str) -> KalturaPartner:
        """Build and configure a KalturaPartner object for sub-tenant creation."""
        partner = KalturaPartner()
        partner.adminEmail = partner_email
        partner.adminName = partner_name
        partner.name = partner_name
        partner.type = KalturaPartnerType.ADMIN_CONSOLE
        partner.partnerParentId = self.partner_id
        partner.description = partner_description or f"{partner_name} child account."
        partner.partnerPackage = 100
        
        # Configure modules and features
        modules_to_enable = [
            "hosted", "theming", "newrow", "chatandcollaboration",
            "embeddedrooms", "Meetingentry", "kaftestme", "kwebcast"
        ]
        
        partner.additionalParams = []
        
        # Add modules parameter
        partner.additionalParams.append(KalturaKeyValue())
        partner.additionalParams[-1].key = "modules"
        partner.additionalParams[-1].value = ",".join(modules_to_enable)
        
        # Enable each module
        for module in modules_to_enable:
            partner.additionalParams.append(KalturaKeyValue())
            partner.additionalParams[-1].key = f"{module}.enabled"
            partner.additionalParams[-1].value = "true"
        
        # Add theming feature
        partner.additionalParams.append(KalturaKeyValue())
        partner.additionalParams[-1].key = "theming.features.mediapage"
        partner.additionalParams[-1].value = "1"
        
        # Add customer partner type
        partner.additionalParams.append(KalturaKeyValue())
        partner.additionalParams[-1].key = "customPartnerType"
        partner.additionalParams[-1].value = "kaf"
        
        return partner
    
    def list_categories(self) -> Dict[str, Any]:
        """
        List all categories for the partner.
        
        Returns:
            Dict[str, Any]: Categories list with metadata
            
        Raises:
            Exception: If category listing fails
        """
        try:
            filter_obj = None  # No filter to get all categories
            pager = KalturaFilterPager()
            pager.pageSize = self.DEFAULT_PAGE_SIZE  # Ensure we get all categories
            pager.pageIndex = self.DEFAULT_PAGE_INDEX
            result = self.client.category.list(filter_obj, pager)

            if not result:
                raise Exception('Failed to list categories: null response')

            # Convert result to JSON-serializable format
            categories = []
            if hasattr(result, 'objects') and result.objects:
                for category in result.objects:
                    categories.append({
                        'id': getattr(category, 'id', None),
                        'parentId': getattr(category, 'parentId', None),
                        'name': getattr(category, 'name', None),
                        'fullName': getattr(category, 'fullName', None),
                        'depth': getattr(category, 'depth', None)
                    })

            response_data = {
                'categories': categories,
                'totalCount': getattr(result, 'totalCount', 0)
            }
            
            print(f"✅ Listed {len(categories)} categories successfully")
            return response_data
            
        except Exception as error:
            print(f"❌ Error listing categories: {error}")
            raise error
    
    def create_publishing_category(self) -> Dict[str, Any]:
        """
        Create a publishing category under the configured customer name hierarchy.
        
        Returns:
            Dict[str, Any]: Created category information
            
        Raises:
            Exception: If category creation fails
        """
        try:
            customer_name = os.environ.get('CUSTOMER_NAME', 'customer_name')
            # Always attempt to locate the customer category hierarchy automatically
            try:
                print(f"🔍 Searching for parent category '{customer_name}>site>channels' ...")

                # Retry logic: attempt to locate the parent category up to 3 times,
                # pausing between attempts in case the category has not
                # yet been created by the instance.
                max_attempts = self.DEFAULT_SEARCH_ATTEMPTS
                for attempt in range(1, max_attempts + 1):
                    cat_filter = KalturaCategoryFilter()
                    cat_filter.fullNameEqual = f"{customer_name}>site>channels"

                    # No pager needed; passing None uses default server-side pagination
                    search_result = self.client.category.list(cat_filter, None)

                    if search_result and hasattr(search_result, 'objects') and search_result.objects:
                        parent_category_id = getattr(search_result.objects[0], 'id', None)
                        print(f"✅ Found parent category with ID: {parent_category_id}")
                        break
                    else:
                        if attempt < max_attempts:
                            print(f"⚠️ Parent category not found (attempt {attempt}/{max_attempts}). Waiting {self.DEFAULT_SEARCH_WAIT_TIME} seconds before retrying...")
                            time.sleep(self.DEFAULT_SEARCH_WAIT_TIME)
                        else:
                            raise Exception(f"Parent category '{customer_name}>site>channels' not found")

            except Exception as search_error:
                print(f"❌ Error locating parent category: {search_error}")
                raise search_error

            # Proceed to create the publishing category under the resolved parent_category_id
            category = KalturaCategory()
            category.parentId = int(parent_category_id)
            category.name = f"{self.partner_id}_CHANNEL_FOR_PUBLISHING_DONT_DELETE"

            result = self.client.category.add(category)

            if not result:
                raise Exception('Failed to create publishing category: null response')

            # Convert result to JSON-serializable format
            category_data = {
                'id': getattr(result, 'id', None),
                'parentId': getattr(result, 'parentId', None),
                'name': getattr(result, 'name', None),
                'fullName': getattr(result, 'fullName', None),
                'partnerId': getattr(result, 'partnerId', None)
            }

            print(f"✅ Publishing category created successfully: {category_data['id']}")
            return category_data
            
        except Exception as error:
            print(f"❌ Error creating publishing category: {error}")
            raise error 

    def check_kaf_instance_ready(self) -> bool:
        """
        Check if KAF instance is ready by calling the version endpoint.
        
        Returns:
            bool: True if instance is ready (HTTP 200 + version), False otherwise
            
        Note:
            This method performs a single check and returns immediately.
            Use in a loop with delays for polling behavior.
        """
        try:
            kaf_url = f"https://{self.partner_id}.kaf.kaltura.com/version"
            
            self.logger.info(f"🔍 Checking KAF instance readiness for partner {self.partner_id}")
            self.logger.info(f"📡 Checking endpoint: {kaf_url}")
            
            response = requests.get(kaf_url, timeout=30)
            
            if response.status_code == 200:
                version = response.text.strip()
                self.logger.info(f"✅ KAF instance is ready! Version: {version}")
                return True
                
            elif response.status_code == 500:
                self.logger.info(f"⏳ KAF instance not ready yet (HTTP 500)")
                return False
            else:
                self.logger.warning(f"⚠️  Unexpected HTTP status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"⚠️  Request failed: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error during KAF check: {str(e)}")
            return False 

 