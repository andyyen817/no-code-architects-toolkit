# Copyright (c) 2025 Stephen G. Pope
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.



import os
import logging
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from config import validate_env_vars

# Conditional imports for cloud services
try:
    from services.gcp_toolkit import upload_to_gcs
    GCP_TOOLKIT_AVAILABLE = True
except ImportError:
    GCP_TOOLKIT_AVAILABLE = False
    upload_to_gcs = None

try:
    from services.s3_toolkit import upload_to_s3
    S3_TOOLKIT_AVAILABLE = True
except ImportError:
    S3_TOOLKIT_AVAILABLE = False
    upload_to_s3 = None

logger = logging.getLogger(__name__)

def parse_s3_url(s3_url):
    """Parse S3 URL to extract bucket name, region, and endpoint URL."""
    parsed_url = urlparse(s3_url)
    
    # Extract bucket name from the host
    bucket_name = parsed_url.hostname.split('.')[0]
    
    # Extract region from the host
    region = parsed_url.hostname.split('.')[1]
    
    return bucket_name, region

class CloudStorageProvider(ABC):
    @abstractmethod
    def upload_file(self, file_path: str) -> str:
        pass

class GCPStorageProvider(CloudStorageProvider):
    def __init__(self):
        self.bucket_name = os.getenv('GCP_BUCKET_NAME')

    def upload_file(self, file_path: str) -> str:
        if not GCP_TOOLKIT_AVAILABLE or upload_to_gcs is None:
            logger.warning("GCP toolkit not available, cannot upload to GCS")
            return None
        return upload_to_gcs(file_path, self.bucket_name)

class S3CompatibleProvider(CloudStorageProvider):
    def __init__(self):

        self.endpoint_url = os.getenv('S3_ENDPOINT_URL')
        self.access_key = os.getenv('S3_ACCESS_KEY')
        self.secret_key = os.getenv('S3_SECRET_KEY')
        self.bucket_name = os.environ.get('S3_BUCKET_NAME', '')
        self.region = os.environ.get('S3_REGION', '')
        
        # Check if endpoint is Digital Ocean and bucket name or region is missing
        if (self.endpoint_url and 
            'digitalocean' in self.endpoint_url.lower() and 
            (not self.bucket_name or not self.region)):
            
            logger.info("Digital Ocean endpoint detected with missing bucket or region. Extracting from URL.")
            try:
                # Extract bucket name and region from URL like https://sgp-labs.nyc3.digitaloceanspaces.com
                parsed_url = urlparse(self.endpoint_url)
                hostname_parts = parsed_url.hostname.split('.')
                
                # The first part is the bucket name (sgp-labs)
                if not self.bucket_name:
                    self.bucket_name = hostname_parts[0]
                    logger.info(f"Extracted bucket name from URL: {self.bucket_name}")
                
                # The second part is the region (nyc3)
                if not self.region:
                    self.region = hostname_parts[1]
                    logger.info(f"Extracted region from URL: {self.region}")
                
            except Exception as e:
                logger.warning(f"Failed to parse Digital Ocean URL: {e}. Using provided values.")

    def upload_file(self, file_path: str) -> str:
        if not S3_TOOLKIT_AVAILABLE or upload_to_s3 is None:
            logger.warning("S3 toolkit not available, cannot upload to S3")
            return None
        return upload_to_s3(file_path, self.endpoint_url, self.access_key, self.secret_key, self.bucket_name, self.region)

class LocalStorageProvider(CloudStorageProvider):
    def __init__(self):
        from config import get_storage_config
        self.upload_folder = get_storage_config()['upload_folder']
        # Ensure the upload folder exists
        os.makedirs(self.upload_folder, exist_ok=True)
        
    def upload_file(self, file_path: str) -> str:
        """Copy file to local storage and return a local URL"""
        import shutil
        import uuid
        
        # Generate unique filename
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Copy to upload folder
        destination = os.path.join(self.upload_folder, unique_filename)
        shutil.copy2(file_path, destination)
        
        # Return local URL (assuming the app serves files from /uploads)
        return f"http://localhost:5000/uploads/{unique_filename}"

def get_storage_provider() -> CloudStorageProvider:
    
    if os.getenv('S3_ENDPOINT_URL') and S3_TOOLKIT_AVAILABLE:

        if ('digitalocean' in os.getenv('S3_ENDPOINT_URL').lower()):

            validate_env_vars('S3_DO')
        else:
            validate_env_vars('S3')

        return S3CompatibleProvider()
    
    if os.getenv('GCP_BUCKET_NAME') and GCP_TOOLKIT_AVAILABLE:

        validate_env_vars('GCP')
        return GCPStorageProvider()
    
    # Fallback to local storage if no cloud storage is configured or toolkits unavailable
    if not S3_TOOLKIT_AVAILABLE and os.getenv('S3_ENDPOINT_URL'):
        logger.warning("S3 toolkit not available, falling back to local storage")
    if not GCP_TOOLKIT_AVAILABLE and os.getenv('GCP_BUCKET_NAME'):
        logger.warning("GCP toolkit not available, falling back to local storage")
    
    logger.info("Using local storage")
    return LocalStorageProvider()

def upload_file(file_path: str) -> str:
    provider = get_storage_provider()
    try:
        logger.info(f"Uploading file to cloud storage: {file_path}")
        url = provider.upload_file(file_path)
        logger.info(f"File uploaded successfully: {url}")
        return url
    except Exception as e:
        logger.error(f"Error uploading file to cloud storage: {e}")
        raise
    