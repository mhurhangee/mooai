"""
file_utils.py
Utilities for handling file attachments in Slack messages.
"""

import base64
import logging
import os
from typing import Dict, List, Optional, Tuple, Any

import requests
from slack_sdk import WebClient

logger = logging.getLogger(__name__)

# Supported file types and their MIME types
SUPPORTED_FILE_TYPES = {
    # Document types
    "pdf": "application/pdf",
    
    # Image types
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "gif": "image/gif",
}


def download_file(client: WebClient, file_info: Dict[str, Any]) -> Optional[Tuple[str, bytes]]:
    """
    Download a file from Slack using the files.info API.
    
    Args:
        client: Slack WebClient instance
        file_info: File information dictionary from Slack event
        
    Returns:
        Tuple of (filename, file_content_bytes) or None if download fails
    """
    try:
        # Get file info which contains the URL
        file_id = file_info.get("id")
        if not file_id:
            logger.error("Missing file ID in file info")
            return None
            
        # Get file info which contains the private URL
        response = client.files_info(file=file_id)
        if not response or not response.get("ok", False):
            logger.error(f"Failed to get file info: {response.get('error', 'Unknown error')}")
            return None
            
        file_data = response.get("file", {})
        url_private = file_data.get("url_private")
        filename = file_data.get("name", "unknown_file")
        
        if not url_private:
            logger.error("No private URL found in file info")
            return None
            
        # Download the file using the bot token for authentication
        headers = {"Authorization": f"Bearer {client.token}"}
        file_response = requests.get(url_private, headers=headers)
        
        if file_response.status_code != 200:
            logger.error(f"Failed to download file: HTTP {file_response.status_code}")
            return None
            
        return filename, file_response.content
        
    except Exception as e:
        logger.exception(f"Error downloading file: {e}")
        return None


def process_file_for_openai(filename: str, file_content: bytes) -> Optional[Dict[str, Any]]:
    """
    Process a file for sending to OpenAI.
    
    Args:
        filename: Name of the file
        file_content: Binary content of the file
        
    Returns:
        Dictionary with file information formatted for OpenAI or None if processing fails
    """
    try:
        # Get file extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower().lstrip(".")
        
        # Check if file type is supported
        if ext not in SUPPORTED_FILE_TYPES:
            logger.warning(f"Unsupported file type: {ext}")
            return None
            
        # Encode file content as base64
        base64_content = base64.b64encode(file_content).decode("utf-8")
        mime_type = SUPPORTED_FILE_TYPES.get(ext)
        
        # Check file size (20MB limit for images)
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > 20 and ext in ["png", "jpg", "jpeg", "webp", "gif"]:
            logger.warning(f"Image file too large: {file_size_mb:.2f}MB (limit: 20MB)")
            return None
        
        # Create appropriate format based on file type
        if ext in ["png", "jpg", "jpeg", "webp", "gif"]:
            return {
                "type": "input_image",
                "image_url": f"data:{mime_type};base64,{base64_content}",
            }
        else:  # PDF and other document types
            return {
                "type": "input_file",
                "filename": filename,
                "file_data": f"data:{mime_type};base64,{base64_content}",
            }
        
    except Exception as e:
        logger.exception(f"Error processing file for OpenAI: {e}")
        return None


def extract_files_from_slack_messages(
    client: WebClient, slack_messages: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract files from Slack messages and organize them by message timestamp.
    
    Args:
        client: Slack WebClient instance
        slack_messages: List of Slack message dictionaries
        
    Returns:
        Dictionary mapping message timestamps to lists of processed files
    """
    files_by_ts = {}
    
    for msg in slack_messages:
        ts = msg.get("ts")
        files = msg.get("files", [])
        
        if not ts or not files:
            continue
            
        processed_files = []
        for file_info in files:
            # Check if file type is supported
            filetype = file_info.get("filetype", "").lower()
            if filetype not in ["pdf", "png", "jpg", "jpeg", "webp", "gif"]:
                logger.info(f"Skipping unsupported file type: {filetype}")
                continue
                
            # Download the file
            download_result = download_file(client, file_info)
            if not download_result:
                continue
                
            filename, file_content = download_result
            
            # Process the file for OpenAI
            processed_file = process_file_for_openai(filename, file_content)
            if processed_file:
                processed_files.append(processed_file)
                
        if processed_files:
            files_by_ts[ts] = processed_files
            
    return files_by_ts
