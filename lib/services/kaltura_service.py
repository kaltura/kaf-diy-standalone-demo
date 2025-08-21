from flask import jsonify, request
from typing import Optional, Dict, Any
from ..models.live_event_model import KalturaLiveEventModel
from ..models.room_model import KalturaRoomModel
from ..models.sub_tenant_model import KalturaSubTenantModel
from ..kaltura_integration.simple_client import get_user_client
import time
import json
import os

class KalturaService:
    """Kaltura service for handling API operations using Service Layer pattern"""
    
    def __init__(self, partner_id: int, kaltura_url: str, admin_secret: str, user_id: str):
        """
        Initialize the service with both live event and room models.
        
        Args:
            partner_id: Kaltura partner ID
            kaltura_url: Kaltura service URL
            admin_secret: Admin secret for authentication
            user_id: User ID for operations
        """
        self.live_model = KalturaLiveEventModel(partner_id, kaltura_url, admin_secret, user_id)
        self.room_model = KalturaRoomModel(partner_id, kaltura_url, admin_secret, user_id)
    
    @classmethod
    def from_request_data(cls, data):
        """Create KalturaService instance from request data with validation"""
        partner_id = data.get('partnerId')
        kaltura_url = data.get('kalturaUrl')
        admin_secret = data.get('adminSecret')
        user_id = data.get('userId')
        
        if not partner_id or not kaltura_url or not admin_secret or not user_id:
            raise ValueError('Missing required Kaltura credentials (partnerId, kalturaUrl, adminSecret, userId).')
        
        return cls(int(partner_id), kaltura_url, admin_secret, user_id)

    @staticmethod
    def _create_sub_tenant_model(data):
        """Create KalturaSubTenantModel instance from request data with validation"""
        partner_id = data.get('partnerId')
        kaltura_url = data.get('kalturaUrl')
        admin_secret = data.get('adminSecret')
        user_id = data.get('userId')
        
        if not partner_id or not kaltura_url or not admin_secret or not user_id:
            raise ValueError('Missing required Kaltura credentials (partnerId, kalturaUrl, adminSecret, userId).')
        
        return KalturaSubTenantModel(
            int(partner_id),
            kaltura_url,
            admin_secret,
            user_id
        )

    @staticmethod
    def generate_session(data):
        """Generate a Kaltura session token for embedded rooms"""
        try:
            # Extract parameters
            partner_id = data.get('partnerId')
            kaltura_url = data.get('kalturaUrl')
            admin_secret = data.get('adminSecret')
            user_id = data.get('userId', '')
            entry_id = data.get('entryId', '')
            role = data.get('role', '')
            first_name = data.get('firstName', '')
            last_name = data.get('lastName', '')
            chat_moderator = data.get('chatModerator', '')
            room_moderator = data.get('roomModerator', '')

            print(f"Creating session: {user_id}")

            # Build privileges string based on parameters to match required format
            privileges_parts = []

            # Add actionslimit (always -1)
            privileges_parts.append("actionslimit:-1")

            # Add user ID if specified
            if user_id:
                privileges_parts.append(f"userId:{user_id}")

            # Add entry ID if specified
            if entry_id:
                privileges_parts.append(f"entryId:{entry_id}")

            # Add firstName and lastName with values if provided
            if first_name:
                privileges_parts.append(f"firstName:{first_name}")
            else:
                privileges_parts.append("firstName")

            if last_name:
                privileges_parts.append(f"lastName:{last_name}")
            else:
                privileges_parts.append("lastName")

            # Add moderator privileges with values if provided
            if chat_moderator:
                privileges_parts.append(f"chatModerator:{chat_moderator}")
            else:
                privileges_parts.append("chatModerator")

            if room_moderator:
                privileges_parts.append(f"roomModerator:{room_moderator}")
            else:
                privileges_parts.append("roomModerator")

            # Add undefined:Submit
            privileges_parts.append("undefined:Submit")

            # Add role if specified
            if role:
                privileges_parts.append(f"role:{role}")

            # Join privileges into string
            privileges_str = ",".join(privileges_parts)

            # Generate user KS using simple client
           
            if not partner_id or not kaltura_url or not admin_secret:
                return jsonify({
                    'success': False,
                    'message': 'Missing required Kaltura credentials (partnerId, kalturaUrl, adminSecret).'
                }), 400
            client = get_user_client(int(partner_id), kaltura_url, admin_secret, user_id or "anonymous", privileges_str, 3600)
            ks = client.getKs()  # Get the KS from the client

            return jsonify({
                'success': True,
                'session': {
                    'ks': ks,
                    'userId': user_id,
                    'entryId': entry_id,
                    'role': role,
                    'firstName': first_name,
                    'lastName': last_name,
                    'chatModerator': chat_moderator,
                    'roomModerator': room_moderator
                }
            }), 200

        except Exception as error:
            print(f'Error creating session: {error}')
            return jsonify({
                'success': False,
                'message': str(error) or 'Failed to create session'
            }), 500
    
    
    
    @staticmethod
    def add_room_session(data):
        """Add a new room entry"""
        try:
            room_name = data.get('roomName')
            room_desc = data.get('roomDesc')
            live_entry_id_input = data.get('liveEntryIdInput', '')
            template_room_entry_id = data.get('templateRoomEntryId', '')

            if not room_name or not room_desc:
                return jsonify({
                    'success': False,
                    'message': 'Missing required parameters: roomName and roomDesc'
                }), 400
            if not template_room_entry_id or not template_room_entry_id.strip():
                return jsonify({
                    'success': False,
                    'message': 'Template Room Entry ID is required for room creation'
                }), 400

            # Use Service Layer to create room
            service = KalturaService.from_request_data(data)
            result = service.room_model.create_room_entry(
                name=room_name,
                description=room_desc,
                live_entry_id_input=live_entry_id_input,
                template_room_entry_id=template_room_entry_id
            )

            return jsonify({
                'success': True,
                'room': result.get('data', {}),
                'message': 'Room created successfully'
            }), 200
        except ValueError as ve:
            return jsonify({'success': False, 'message': str(ve)}), 400
        except Exception as error:
            print(f'Error creating room: {error}')
            return jsonify({
                'success': False,
                'message': str(error) or 'Failed to create room'
            }), 500

    @staticmethod
    def create_diy(data):
        """Create a room with automatic live entry creation using Service Layer orchestration"""
        try:
            # Import here to avoid circular imports
            from ..routes import send_progress_update
            
            send_progress_update("🚀 Starting DIY room creation process...", "start")
            print("🚀 Starting create_diy process...")
            
            room_name = data.get('roomName')
            room_desc = data.get('roomDesc')

            if not room_name or not room_desc:
                send_progress_update("❌ Missing required parameters: roomName and roomDesc", "error")
                return jsonify({
                    'success': False,
                    'message': 'Missing required parameters: roomName and roomDesc'
                }), 400

            # Get category ID from request data
            category_id = data.get('categoryId')

            # Get template room entry ID from environment variable
            template_room_entry_id = os.getenv('TEMPLATE_ROOM_ENTRY_ID')
            if not template_room_entry_id:
                send_progress_update("❌ Template Room Entry ID not configured", "error")
                return jsonify({
                    'success': False,
                    'message': 'Template Room Entry ID not configured. Please set TEMPLATE_ROOM_ENTRY_ID environment variable.'
                }), 400

            # Use Service Layer to orchestrate both live entry and room creation
            service = KalturaService.from_request_data(data)
            result = service._create_diy_orchestration(
                name=room_name,
                description=room_desc,
                template_room_entry_id=template_room_entry_id,
                user_id=data.get('userId'),
                category_id=data.get('categoryId')
            )

            print(f"✅ Room with live entry created successfully")

            return jsonify(result), 200
        except ValueError as ve:
            error_msg = f"❌ Validation error: {ve}"
            send_progress_update(error_msg, "error")
            print(f"❌ Validation error: {ve}")
            return jsonify({'success': False, 'message': str(ve)}), 400
        except Exception as error:
            error_msg = f'❌ Error creating room with live entry: {error}'
            send_progress_update(error_msg, "error")
            print(f'❌ Error creating room with live entry: {error}')
            return jsonify({
                'success': False,
                'message': str(error) or 'Failed to create room with live entry'
            }), 500
    

    @staticmethod
    def get_session_details(data):
        """Get session details by entry ID"""
        try:
            entry_id = data.get('entryId')
            
            if not entry_id:
                return jsonify({
                    'success': False,
                    'message': 'Entry ID is required'
                }), 400
            
            # Use Service Layer to get session details
            service = KalturaService.from_request_data(data)
            result = service.live_model.get_session(entry_id)
            
            return jsonify({
                'success': True,
                'event': result
            }), 200
            
        except ValueError as ve:
            return jsonify({'success': False, 'message': str(ve)}), 400
        except Exception as error:
            error_message = str(error)
            print(f'Error getting session details: {error_message}')
            return jsonify({
                'success': False,
                'message': error_message,
                'error': 'ENTRY_NOT_FOUND' if 'not found' in error_message.lower() else 'UNKNOWN_ERROR'
            }), 404 if 'not found' in error_message.lower() else 500
    
    @staticmethod
    def add_live_session(data):
        """Add a new live session"""
        try:
            session_name = data.get('sessionName')
            session_description = data.get('sessionDescription')
            category_id = data.get('categoryId')  # Get category ID from request data
            
            if not session_name or not session_description:
                return jsonify({
                    'success': False,
                    'message': 'Missing required parameters: sessionName and sessionDescription'
                }), 400

            # Use Service Layer to create live entry
            service = KalturaService.from_request_data(data)
            live_stream_response = service.live_model.create_live_entry(
                event_name=session_name,
                event_description=session_description,
                user_id=data.get('userId'),
                category_id=category_id  # Pass category_id to create_live_entry
            )

            if not live_stream_response:
                raise Exception('Failed to create live entry: null response')

            return jsonify({
                'success': True,
                'event': {
                    'id': live_stream_response.id,
                    'name': live_stream_response.name,
                    'description': live_stream_response.description,
                }
            }), 200
        except ValueError as ve:
            return jsonify({'success': False, 'message': str(ve)}), 400
        except Exception as error:
            print(f'Error creating live session: {error}')
            return jsonify({
                'success': False,
                'message': str(error) or 'Failed to create live session'
            }), 500
    
    def _create_diy_orchestration(
        self, 
        name: str, 
        description: str,
        template_room_entry_id: str,
        user_id: Optional[str] = None, 
        category_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate the creation of both live entry and room.
        
        This method coordinates between the live event model and room model
        to create a complete DIY event with both components.
        
        Args:
            name: The name for both live entry and room
            description: The description for both live entry and room
            template_room_entry_id: Template room entry ID to use
            user_id: The user ID for the live entry (optional)
            category_id: The category ID to add the live entry to (optional)
            
        Returns:
            Dict[str, Any]: Combined result with both live entry and room data
            
        Raises:
            Exception: If the creation process fails
        """
        # Import here to avoid circular imports
        from ..routes import send_progress_update
        
        print("🚀 Starting create_diy orchestration...")
        
        try:
            # Step 1: Create live entry
            send_progress_update("📺 Step 1: Creating live entry...", "live_entry_start")
            print("📺 Creating live entry...")
            live_stream_response = self.live_model.create_live_entry(
                event_name=name,
                event_description=description,
                user_id=user_id,
                category_id=category_id
            )

            if not live_stream_response or not hasattr(live_stream_response, 'id'):
                send_progress_update("❌ Failed to create live entry: invalid response", "live_entry_error")
                raise Exception('Failed to create live entry: invalid response')

            live_entry_id = live_stream_response.id
            send_progress_update(f"✅ Live entry created successfully with ID: {live_entry_id}", "live_entry_success")
            print(f"✅ Live entry created successfully with ID: {live_entry_id}")

            # Step 2: Create room with live entry
            send_progress_update("🏗️ Step 2: Creating room with live entry...", "room_creation_start")
            print("🏗️ Creating room with live entry...")
            room_result = self.room_model.create_room_entry(
                name=name,
                description=description,
                live_entry_id_input=live_entry_id,
                template_room_entry_id=template_room_entry_id
            )

            send_progress_update("✅ Room created successfully", "room_creation_success")
            print(f"✅ Room created successfully")

            # Return combined result
            result = {
                'success': True,
                'live_entry': {
                    'id': live_entry_id,
                    'name': live_stream_response.name,
                    'description': live_stream_response.description
                },
                'room': room_result.get('data', {}),
                'message': 'Room created successfully with live entry'
            }
            
            # Send clean summary
            room_id = room_result.get('data', {}).get('id', 'Unknown')
            send_progress_update(f"🎉 DIY creation completed successfully!", "diy_complete")
            send_progress_update(f"📺 Live Entry: {live_entry_id} ({live_stream_response.name})", "summary")
            send_progress_update(f"🏗️ Room: {room_id} ({name}_studio)", "summary")
            send_progress_update(f"🔧 Room Template used: {template_room_entry_id}", "summary")
            
            return result
            
        except Exception as error:
            send_progress_update(f"❌ Error in create_diy orchestration: {error}", "diy_error")
            print(f"❌ Error in create_diy orchestration: {error}")
            raise error
    
    @staticmethod
    def create_sub_tenant(data):
        """Create a new Kaltura sub-tenant and publishing category"""
        try:
            # Extract parameters, falling back to environment variables 
            user_id = os.getenv('KALTURA_USER_ID')
            parent_partner_id = os.getenv('KALTURA_PARENT_PARTNER_ID')
            kaltura_url = os.getenv('KALTURA_URL')
            admin_secret = os.getenv('KALTURA_ADMIN_SECRET')
            partner_name = os.getenv('KALTURA_PARTNER_NAME')
            partner_email = os.getenv('KALTURA_PARTNER_EMAIL')
            partner_description = os.getenv('KALTURA_PARTNER_DESCRIPTION', '')
            template_partner_id = os.getenv('KALTURA_TEMPLATE_PARTNER_ID')

            # Validate required fields after env fallback
            if not all([user_id, parent_partner_id, kaltura_url, admin_secret, partner_name, partner_email, template_partner_id]):
                return jsonify({'success': False, 'message': 'Missing required Kaltura credentials or parameters. Please set the appropriate environment variables.'}), 400

            # Create sub-tenant model for authentication - use parent_partner_id since we're creating under the parent
            tenant_data = {
                'partnerId': parent_partner_id,
                'kalturaUrl': kaltura_url,
                'adminSecret': admin_secret,
                'userId': user_id
            }
            sub_tenant_model = KalturaService._create_sub_tenant_model(tenant_data)
            
            # Use SubTenantModel to create sub-tenant
            tenant_response = sub_tenant_model.create_sub_tenant(
                partner_name=partner_name,
                partner_email=partner_email,
                template_partner_id=int(template_partner_id),
                partner_description=partner_description
            )
            
            # Now create the publishing category using the NEW sub-tenant credentials
            # Extract the new sub-tenant's credentials from the response
            new_partner_id = tenant_response.get('id')
            new_admin_secret = tenant_response.get('adminSecret')
            new_admin_user_id = tenant_response.get('adminUserId')
            
            if not all([new_partner_id, new_admin_secret, new_admin_user_id]):
                raise Exception('Failed to extract new sub-tenant credentials from response')
            
            # Create a new sub-tenant model with the new sub-tenant's credentials
            new_tenant_data = {
                'partnerId': str(new_partner_id),
                'kalturaUrl': kaltura_url,
                'adminSecret': new_admin_secret,
                'userId': new_admin_user_id
            }
            new_sub_tenant_model = KalturaService._create_sub_tenant_model(new_tenant_data)
            
            # Check if KAF instance is ready using the sub-tenant model
            kaf_status = None
            try:
                print("🔍 Checking if KAF instance is ready...")
                
                # Use the sub-tenant model to check KAF readiness
                start_time = time.time()
                max_wait_time = 100      
                check_interval = 30    # 10 second
                attempts = 0
                
                while True:
                    attempts += 1
                    elapsed_time = time.time() - start_time
                    
                    print(f"🔄 Attempt {attempts}: Checking KAF instance (elapsed: {elapsed_time:.1f}s)")
                    
                    # Check if KAF instance is ready
                    is_ready = new_sub_tenant_model.check_kaf_instance_ready()
                    
                    if is_ready:
                        print(f"✅ KAF instance is ready!")
                        print(f"🎉 Total time: {elapsed_time:.1f} seconds, Total attempts: {attempts}")
                        
                        # Automate embedded rooms setup now that KAF is ready
                        try:

                             # Create the publishing category using the new sub-tenant's credentials
                            category_data = new_sub_tenant_model.create_publishing_category()
                            print(f"✅ Publishing category created: {category_data}")

                            print("🔧 Starting embedded rooms automation setup...")
                            automation_result = new_sub_tenant_model.automate_embedded_rooms_setup()
                            print(f"✅ Embedded rooms automation completed: {automation_result}")
                            
                           
                            
                        except Exception as automation_error:
                            print(f"⚠️  Embedded rooms automation failed: {automation_error}")
                            # Continue with the process even if automation fails
                        
                        kaf_status = {
                            'success': True,
                            'partner_id': int(new_partner_id),
                            'version': 'Ready',
                            'total_time_seconds': elapsed_time,
                            'total_attempts': attempts,
                            'kaf_url': f"https://{new_partner_id}.kaf.kaltura.com/version"
                        }
                        break
                    
                    else:
                        print(f"⏳ KAF instance not ready yet - attempt {attempts}")
                        
                        # Check if we've exceeded max wait time
                        if elapsed_time >= max_wait_time:
                            error_msg = f"KAF instance not ready after {max_wait_time} seconds ({attempts} attempts)"
                            print(f"❌ {error_msg}")
                            raise Exception(error_msg)
                        
                        # Wait before next check
                        if elapsed_time + check_interval < max_wait_time:
                            print(f"⏳ Waiting {check_interval} seconds before next check...")
                            time.sleep(check_interval)
                        else:
                            # Don't sleep if we're about to hit max wait time
                            break
                            
            except Exception as kaf_error:
                print(f"⚠️  KAF instance readiness check failed: {kaf_error}")
                print("💡 You can manually check later using the check_kaf_instance_ready method")
                kaf_status = {'success': False, 'error': str(kaf_error)}
            
            return jsonify({
                'success': True,
                'result': tenant_response,
                'category': category_data,
                'kaf_status': kaf_status
            }), 200
        except ValueError as ve:
            return jsonify({'success': False, 'message': str(ve)}), 400
        except Exception as error:
            print(f'Error creating sub-tenant and category: {error}')
            return jsonify({
                'success': False,
                'message': str(error) or 'Failed to create sub-tenant and category'
            }), 500



    @staticmethod
    def create_publishing_category(data):
        """Create a publishing category under MediaSpace>site>channels"""
        try:
            # Use SubTenantModel for authentication and category creation
            # The create_publishing_category method automatically finds the parent category
            sub_tenant_model = KalturaService._create_sub_tenant_model(data)


            
            category_data = sub_tenant_model.create_publishing_category()

            return jsonify({
                'success': True,
                'category': category_data
            }), 200

        except ValueError as ve:
            return jsonify({'success': False, 'message': str(ve)}), 400
        except Exception as error:
            print(f'Error creating publishing category: {error}')
            return jsonify({
                'success': False,
                'message': str(error) or 'Failed to create publishing category'
            }), 500

    @staticmethod
    def check_kaf_readiness_endpoint(data):
        """Standalone endpoint to check KAF instance readiness"""
        try:
            partner_id = data.get('partnerId')
            max_wait_time = data.get('maxWaitTime', 300)  # Default 5 minutes
            check_interval = data.get('checkInterval', 10)  # Default 5 seconds
            
            if not partner_id:
                return jsonify({'success': False, 'message': 'Missing required parameter: partnerId'}), 400
            
            try:
                partner_id_int = int(partner_id)
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid partnerId: must be a number'}), 400
            
            # Create a temporary sub-tenant model for checking
            temp_data = {
                'partnerId': str(partner_id_int),
                'kalturaUrl': 'https://www.kaltura.com',  # Dummy URL
                'adminSecret': 'dummy',  # Dummy secret
                'userId': 'dummy'  # Dummy user ID
            }
            
            temp_sub_tenant_model = KalturaService._create_sub_tenant_model(temp_data)
            
            # Check KAF instance readiness using the sub-tenant model
            start_time = time.time()
            attempts = 0
            
            while True:
                attempts += 1
                elapsed_time = time.time() - start_time
                
                print(f"🔄 Attempt {attempts}: Checking KAF instance (elapsed: {elapsed_time:.1f}s)")
                
                # Check if KAF instance is ready
                is_ready = temp_sub_tenant_model.check_kaf_instance_ready()
                
                if is_ready:
                    print(f"✅ KAF instance is ready!")
                    print(f"🎉 Total time: {elapsed_time:.1f} seconds, Total attempts: {attempts}")
                    
                    kaf_status = {
                        'success': True,
                        'partner_id': partner_id_int,
                        'version': 'Ready',
                        'total_time_seconds': elapsed_time,
                        'total_attempts': attempts,
                        'kaf_url': f"https://{partner_id_int}.kaf.kaltura.com/version"
                    }
                    break
                
                else:
                    print(f"⏳ KAF instance not ready yet - attempt {attempts}")
                    
                    # Check if we've exceeded max wait time
                    if elapsed_time >= max_wait_time:
                        error_msg = f"KAF instance not ready after {max_wait_time} seconds ({attempts} attempts)"
                        print(f"❌ {error_msg}")
                        raise Exception(error_msg)
                    
                    # Wait before next check
                    if elapsed_time + check_interval < max_wait_time:
                        print(f"⏳ Waiting {check_interval} seconds before next check...")
                        time.sleep(check_interval)
                    else:
                        # Don't sleep if we're about to hit max wait time
                        break
            
            return jsonify({
                'success': True,
                'kaf_status': kaf_status
            }), 200
            
        except ValueError as ve:
            return jsonify({'success': False, 'message': str(ve)}), 400
        except Exception as error:
            print(f'Error checking KAF instance readiness: {error}')
            return jsonify({
                'success': False,
                'message': str(error) or 'Failed to check KAF instance readiness'
            }), 500 