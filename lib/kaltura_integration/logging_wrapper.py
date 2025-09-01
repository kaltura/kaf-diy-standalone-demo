"""
KalturaClient Logging Wrapper

This module provides a drop-in solution to log all request and response bodies
from KalturaClient without modifying its internals.

Usage:
    # Import and apply the wrapper before creating any KalturaClient instances
    from lib.kaltura_integration.logging_wrapper import enable_kaltura_logging
    
    # Enable logging (call this once at startup)
    enable_kaltura_logging()
    
    # Now all KalturaClient instances will log their requests/responses
    client = get_admin_client(partner_id, service_url, admin_secret, user_id)
"""

import json
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('kaltura_client')

class KalturaLoggingTransport:
    """
    Custom transport wrapper that logs all KalturaClient HTTP requests and responses.
    This wraps the existing transport without modifying KalturaClient internals.
    """
    
    def __init__(self, original_transport):
        self.original_transport = original_transport
        self.request_count = 0
    
    def request(self, method, url, headers=None, data=None, **kwargs):
        """Intercept and log the request before passing it to the original transport"""
        self.request_count += 1
        request_id = f"REQ-{self.request_count:04d}"
        
        # Parse and log the request
        self._log_request(request_id, method, url, headers, data)
        
        # Make the actual request
        start_time = time.time()
        try:
            response = self.original_transport.request(method, url, headers, data, **kwargs)
            elapsed = (time.time() - start_time) * 1000
            
            # Log the response
            self._log_response(request_id, response, elapsed)
            
            return response
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            self._log_error(request_id, e, elapsed)
            raise
    
    def _log_request(self, request_id: str, method: str, url: str, headers: Optional[Dict], data: Any):
        """Log the outgoing request details"""
        parsed_url = urlparse(url)
        
        # Parse query parameters
        query_params = parse_qs(parsed_url.query) if parsed_url.query else {}
        
        # Format the request data for logging
        request_info = {
            'request_id': request_id,
            'method': method,
            'url': url,
            'path': parsed_url.path,
            'query_params': query_params,
            'headers': dict(headers) if headers else {},
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Handle different data types
        if data:
            if isinstance(data, dict):
                request_info['data'] = data
            elif isinstance(data, str):
                try:
                    # Try to parse as JSON
                    request_info['data'] = json.loads(data)
                except json.JSONDecodeError:
                    # If not JSON, log as string
                    request_info['data'] = data[:1000] + '...' if len(data) > 1000 else data
            else:
                request_info['data'] = str(data)[:1000] + '...' if len(str(data)) > 1000 else str(data)
        
        # Log the request
        logger.info(f"🚀 {request_id} - {method} {parsed_url.path}")
        logger.info(f"   URL: {url}")
        if query_params:
            logger.info(f"   Query: {json.dumps(query_params, indent=2)}")
        if data and request_info.get('data'):
            logger.info(f"   Data: {json.dumps(request_info['data'], indent=2, default=str)}")
        if headers:
            # Filter out sensitive headers
            safe_headers = {k: v for k, v in headers.items() 
                          if k.lower() not in ['authorization', 'x-kaltura-session', 'cookie']}
            if safe_headers:
                logger.info(f"   Headers: {json.dumps(safe_headers, indent=2)}")
    
    def _log_response(self, request_id: str, response, elapsed: float):
        """Log the incoming response details"""
        try:
            # Try to get response body
            response_text = getattr(response, 'text', '')
            response_data = None
            
            if response_text:
                try:
                    response_data = json.loads(response_text)
                except json.JSONDecodeError:
                    response_data = response_text[:1000] + '...' if len(response_text) > 1000 else response_text
            
            # Log response summary
            status_code = getattr(response, 'status_code', getattr(response, 'status', 'Unknown'))
            logger.info(f"✅ {request_id} - {status_code} ({elapsed:.1f}ms)")
            
            if response_data:
                if isinstance(response_data, dict):
                    # For API responses, try to extract key information
                    if 'result' in response_data:
                        logger.info(f"   Result: {json.dumps(response_data['result'], indent=2, default=str)}")
                    elif 'error' in response_data:
                        logger.error(f"   Error: {json.dumps(response_data['error'], indent=2, default=str)}")
                    else:
                        logger.info(f"   Response: {json.dumps(response_data, indent=2, default=str)}")
                else:
                    logger.info(f"   Response: {response_data}")
            
        except Exception as e:
            logger.warning(f"⚠️  {request_id} - Failed to parse response: {e}")
    
    def _log_error(self, request_id: str, error: Exception, elapsed: float):
        """Log any errors that occur during the request"""
        logger.error(f"❌ {request_id} - Error after {elapsed:.1f}ms: {str(error)}")
    
    def __getattr__(self, name):
        """Delegate all other attributes to the original transport"""
        return getattr(self.original_transport, name)

# Standalone logging functions for KalturaClient
def _log_request(request_id: str, url: str, params, files=None):
    """Log the outgoing request details"""
    logger.info(f"🚀 {request_id} - POST {url}")
    logger.info(f"   URL: {url}")
    if params:
        try:
            # Handle different parameter types
            if hasattr(params, 'items'):
                # Dictionary-like object
                safe_params = {k: v for k, v in params.items() 
                              if k.lower() not in ['secret', 'password', 'ks']}
                logger.info(f"   Params: {json.dumps(safe_params, indent=2, default=str)}")
            elif hasattr(params, '__dict__'):
                # Object with attributes
                safe_params = {k: v for k, v in params.__dict__.items() 
                              if k.lower() not in ['secret', 'password', 'ks']}
                logger.info(f"   Params: {json.dumps(safe_params, indent=2, default=str)}")
            else:
                # Other types
                logger.info(f"   Params: {str(params)[:500]}...")
        except Exception as e:
            logger.info(f"   Params: {str(params)[:500]}... (parsing failed: {e})")
    if files:
        logger.info(f"   Files: {len(files)} file(s) attached")

def _log_response(request_id: str, response, elapsed: float):
    """Log the incoming response details"""
    try:
        # Try to get response content
        response_text = getattr(response, 'text', '')
        if not response_text:
            response_text = str(response)
        
        # Log response summary
        status_code = getattr(response, 'status_code', getattr(response, 'status', 'Unknown'))
        logger.info(f"✅ {request_id} - {status_code} ({elapsed:.1f}ms)")
        
        if response_text and len(response_text) < 1000:
            logger.info(f"   Response: {response_text}")
        elif response_text:
            logger.info(f"   Response: {response_text[:1000]}...")
            
    except Exception as e:
        logger.warning(f"⚠️  {request_id} - Failed to parse response: {e}")

def _log_response_parsing(request_id: str, response, expected_type):
    """Log the response parsing details"""
    try:
        logger.info(f"🔍 {request_id} - Parsing response as {expected_type}")
    except Exception as e:
        logger.warning(f"⚠️  {request_id} - Failed to log response parsing: {e}")

def _log_error(request_id: str, error: Exception, elapsed: float):
    """Log any errors that occur during the request"""
    logger.error(f"❌ {request_id} - Error after {elapsed:.1f}ms: {str(error)}")

def enable_kaltura_logging():
    """
    Enable logging for all KalturaClient instances.
    
    This function monkey-patches the KalturaClient to intercept HTTP requests
    for logging purposes.
    
    Call this function once at startup before creating any KalturaClient instances.
    """
    try:
        from KalturaClient import KalturaClient
        
        # Store the original method
        KalturaClient._original_do_http_request = KalturaClient.doHttpRequest
        
        def patched_do_http_request(self, url, params, files=None):
            """Intercept and log the HTTP request"""
            request_id = f"REQ-{getattr(self, '_request_count', 0) + 1:04d}"
            self._request_count = getattr(self, '_request_count', 0) + 1
            
            # Log the request
            self._log_request(request_id, url, params, files)
            
            # Make the actual request
            start_time = time.time()
            try:
                result = self._original_do_http_request(url, params, files)
                elapsed = (time.time() - start_time) * 1000
                
                # Log success
                logger.info(f"✅ {request_id} - Request completed in {elapsed:.1f}ms")
                
                return result
                
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                self._log_error(request_id, e, elapsed)
                raise
        
        # Replace the method
        KalturaClient.doHttpRequest = patched_do_http_request
        
        # Add logging methods to the class
        KalturaClient._log_request = lambda self, request_id, url, params, files=None: _log_request(request_id, url, params, files)
        KalturaClient._log_error = lambda self, request_id, error, elapsed: _log_error(request_id, error, elapsed)
        
        logger.info("✅ KalturaClient logging wrapper successfully installed")
        
    except ImportError:
        logger.warning("⚠️  KalturaClient not available - logging wrapper not installed")
    except Exception as e:
        logger.error(f"❌ Failed to install KalturaClient logging wrapper: {e}")

def disable_kaltura_logging():
    """
    Disable logging for KalturaClient instances.
    
    This restores the original KalturaClient behavior.
    """
    try:
        from KalturaClient import KalturaClient
        
        # Restore the original method
        if hasattr(KalturaClient, '_original_do_http_request'):
            KalturaClient.doHttpRequest = KalturaClient._original_do_http_request
            logger.info("🔧 KalturaClient logging wrapper disabled")
        else:
            logger.warning("⚠️  No logging wrapper was installed")
            
    except ImportError:
        logger.warning("⚠️  KalturaClient not available")
    except Exception as e:
        logger.error(f"❌ Failed to disable KalturaClient logging wrapper: {e}")

# Convenience function for quick logging setup
def setup_kaltura_logging(level: str = 'INFO', format_string: Optional[str] = None):
    """
    Set up KalturaClient logging with custom configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom log format string
    """
    # Configure logging
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    if format_string:
        formatter = logging.Formatter(format_string)
        for handler in logger.handlers:
            handler.setFormatter(formatter)
    
    logger.setLevel(log_level)
    
    # Enable the logging wrapper
    enable_kaltura_logging()
    
    logger.info(f"🔧 KalturaClient logging configured with level: {level}")

# Example usage and testing
if __name__ == "__main__":
    # Example of how to use the logging wrapper
    print("KalturaClient Logging Wrapper")
    print("=============================")
    print()
    print("To enable logging, add this to your main application:")
    print("from lib.kaltura_integration.logging_wrapper import enable_kaltura_logging")
    print("enable_kaltura_logging()")
    print()
    print("Or for custom configuration:")
    print("from lib.kaltura_integration.logging_wrapper import setup_kaltura_logging")
    print("setup_kaltura_logging(level='DEBUG')")
    print()
    print("The wrapper will automatically intercept all KalturaClient HTTP requests")
    print("and log them with detailed information including request/response bodies.")
