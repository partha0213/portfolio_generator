"""
Asset Service - Handle image uploads and asset management

Uses Cloudinary for cloud storage of portfolio assets (images, logos, etc.)
"""

import os
import io
from typing import Optional
from fastapi import UploadFile
import cloudinary
import cloudinary.uploader


class AssetService:
    """Handle image uploads and asset management using Cloudinary"""
    
    def __init__(self):
        """Initialize Cloudinary with environment variables"""
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")
        
        if cloud_name and api_key and api_secret:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret
            )
            self.configured = True
        else:
            self.configured = False
    
    async def upload_image(
        self,
        file: UploadFile,
        folder: str = "portfolios",
        public_id: Optional[str] = None
    ) -> dict:
        """
        Upload image to Cloudinary.
        
        Args:
            file: Uploaded file object
            folder: Cloudinary folder path
            public_id: Optional custom public ID
        
        Returns:
            Upload result with URL and metadata
        """
        
        if not self.configured:
            return {
                "success": False,
                "error": "Cloudinary not configured. Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET"
            }
        
        try:
            # Read file content
            content = await file.read()
            
            # Prepare upload options
            upload_options = {
                "folder": folder,
                "resource_type": "auto",
                "quality": "auto:good",
                "fetch_format": "auto"
            }
            
            if public_id:
                upload_options["public_id"] = public_id
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                io.BytesIO(content),
                **upload_options
            )
            
            return {
                "success": True,
                "url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "filename": file.filename,
                "size_bytes": len(content),
                "content_type": file.content_type,
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format")
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filename": file.filename
            }
    
    async def upload_multiple(
        self,
        files: list,
        folder: str = "portfolios"
    ) -> dict:
        """
        Upload multiple images at once.
        
        Args:
            files: List of UploadFile objects
            folder: Cloudinary folder path
        
        Returns:
            Results for each file
        """
        
        results = []
        for file in files:
            result = await self.upload_image(file, folder)
            results.append(result)
        
        successful = sum(1 for r in results if r.get("success"))
        
        return {
            "total_files": len(files),
            "successful": successful,
            "failed": len(files) - successful,
            "results": results
        }
    
    def delete_asset(self, public_id: str) -> dict:
        """
        Delete asset from Cloudinary.
        
        Args:
            public_id: Cloudinary public ID of file to delete
        
        Returns:
            Deletion result
        """
        
        if not self.configured:
            return {
                "success": False,
                "error": "Cloudinary not configured"
            }
        
        try:
            result = cloudinary.uploader.destroy(public_id)
            return {
                "success": result.get("result") == "ok",
                "public_id": public_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_asset_url(
        self,
        public_id: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        quality: str = "auto"
    ) -> str:
        """
        Generate optimized URL for asset with transformations.
        
        Args:
            public_id: Cloudinary public ID
            width: Optional width for resize
            height: Optional height for resize
            quality: Quality setting (auto, high, low)
        
        Returns:
            Optimized Cloudinary URL
        """
        
        transformations = {
            "quality": quality,
            "fetch_format": "auto"
        }
        
        if width:
            transformations["width"] = width
        if height:
            transformations["height"] = height
        
        if width and height:
            transformations["crop"] = "fill"
        
        return cloudinary.CloudinaryImage(public_id).build_url(**transformations)
    
    def validate_image_file(self, file: UploadFile) -> tuple[bool, str]:
        """
        Validate uploaded image file.
        
        Args:
            file: Uploaded file to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/svg+xml",
            "image/gif"
        ]
        
        if file.content_type not in allowed_types:
            return False, f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        
        # Check file size (max 10MB)
        if file.size and file.size > 10 * 1024 * 1024:
            return False, "File size exceeds 10MB limit"
        
        return True, ""
    
    async def upload_with_validation(
        self,
        file: UploadFile,
        folder: str = "portfolios"
    ) -> dict:
        """
        Upload image with validation.
        
        Args:
            file: Uploaded file
            folder: Cloudinary folder
        
        Returns:
            Upload result or validation error
        """
        
        is_valid, error_msg = self.validate_image_file(file)
        
        if not is_valid:
            return {
                "success": False,
                "error": error_msg
            }
        
        return await self.upload_image(file, folder)
