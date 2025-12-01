"""
Assets Router - Handle portfolio asset uploads and management

Manages image uploads, logos, and other portfolio assets via Cloudinary.
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User, Asset
from routers.history import get_current_user
from services.asset_service import AssetService
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.post("/upload")
async def upload_asset(
    file: UploadFile = File(...),
    asset_type: str = Query("image", description="Type of asset: image, logo, icon"),
    session_id: Optional[str] = Query(None, description="Associated session ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload portfolio asset (image, logo, etc.).
    
    Args:
        file: Image file to upload
        asset_type: Type of asset (image, logo, icon)
        session_id: Optional session ID to associate
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Asset upload result with URL
    
    Example:
        ```
        POST /api/assets/upload
        Content-Type: multipart/form-data
        
        file: <binary image data>
        asset_type: image
        session_id: abc123
        ```
    """
    
    try:
        # Validate file
        asset_service = AssetService()
        is_valid, error_msg = asset_service.validate_image_file(file)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Upload to Cloudinary
        upload_result = await asset_service.upload_image(
            file=file,
            folder=f"portfolios/{current_user.id}"
        )
        
        if not upload_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Upload failed: {upload_result.get('error')}"
            )
        
        # Save to database
        asset = Asset(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            session_id=session_id,
            asset_type=asset_type,
            filename=file.filename,
            url=upload_result["url"],
            size_bytes=upload_result.get("size_bytes", 0),
            content_type=file.content_type
        )
        
        db.add(asset)
        await db.commit()
        
        print(f"✅ Asset uploaded: {file.filename} ({upload_result.get('size_bytes')} bytes)")
        
        return {
            "success": True,
            "asset_id": asset.id,
            "url": asset.url,
            "filename": asset.filename,
            "size_bytes": asset.size_bytes,
            "type": asset_type,
            "uploaded_at": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Asset upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-multiple")
async def upload_multiple_assets(
    files: list = File(...),
    asset_type: str = Query("image"),
    session_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload multiple assets at once.
    
    Args:
        files: List of image files
        asset_type: Type of all assets
        session_id: Optional session ID
        db: Database session
        current_user: Current user
    
    Returns:
        Results for each uploaded file
    """
    
    try:
        asset_service = AssetService()
        results = []
        
        for file in files:
            # Validate
            is_valid, error_msg = asset_service.validate_image_file(file)
            
            if not is_valid:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": error_msg
                })
                continue
            
            # Upload
            upload_result = await asset_service.upload_image(
                file=file,
                folder=f"portfolios/{current_user.id}"
            )
            
            if upload_result.get("success"):
                # Save to database
                asset = Asset(
                    id=str(uuid.uuid4()),
                    user_id=current_user.id,
                    session_id=session_id,
                    asset_type=asset_type,
                    filename=file.filename,
                    url=upload_result["url"],
                    size_bytes=upload_result.get("size_bytes", 0),
                    content_type=file.content_type
                )
                db.add(asset)
                
                results.append({
                    "filename": file.filename,
                    "success": True,
                    "asset_id": asset.id,
                    "url": upload_result["url"],
                    "size_bytes": upload_result.get("size_bytes", 0)
                })
            else:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": upload_result.get("error")
                })
        
        await db.commit()
        
        successful = sum(1 for r in results if r.get("success"))
        print(f"✅ Batch upload: {successful}/{len(files)} files uploaded")
        
        return {
            "total_files": len(files),
            "successful": successful,
            "failed": len(files) - successful,
            "results": results
        }
    
    except Exception as e:
        print(f"❌ Batch upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")


@router.get("/list")
async def list_assets(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all assets for current user.
    
    Args:
        session_id: Optional filter by session
        asset_type: Optional filter by type
        db: Database session
        current_user: Current user
    
    Returns:
        List of assets
    """
    
    try:
        query = Asset.__table__.select().where(Asset.user_id == current_user.id)
        
        if session_id:
            query = query.where(Asset.session_id == session_id)
        if asset_type:
            query = query.where(Asset.asset_type == asset_type)
        
        result = await db.execute(query.order_by(Asset.created_at.desc()))
        assets = result.fetchall()
        
        return {
            "success": True,
            "total": len(assets),
            "assets": [
                {
                    "id": asset[0],
                    "filename": asset[3],
                    "url": asset[4],
                    "type": asset[2],
                    "size_bytes": asset[5],
                    "created_at": asset[7].isoformat() if asset[7] else None
                }
                for asset in assets
            ]
        }
    
    except Exception as e:
        print(f"❌ List assets error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete asset by ID.
    
    Args:
        asset_id: Asset ID to delete
        db: Database session
        current_user: Current user
    
    Returns:
        Deletion confirmation
    """
    
    try:
        # Check ownership
        result = await db.execute(
            Asset.__table__.select()
            .where((Asset.id == asset_id) & (Asset.user_id == current_user.id))
        )
        asset = result.fetchone()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Delete from Cloudinary
        asset_service = AssetService()
        public_id = asset[0]  # Assuming public_id is stored
        
        # Delete from database
        await db.execute(Asset.__table__.delete().where(Asset.id == asset_id))
        await db.commit()
        
        print(f"✅ Asset deleted: {asset_id}")
        
        return {
            "success": True,
            "asset_id": asset_id,
            "message": "Asset deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Asset deletion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cloudinary/url-preview")
async def get_optimized_url(
    public_id: str = Query(..., description="Cloudinary public ID"),
    width: Optional[int] = Query(None, description="Resize width"),
    height: Optional[int] = Query(None, description="Resize height"),
    current_user: User = Depends(get_current_user)
):
    """
    Get optimized Cloudinary URL with transformations.
    
    Args:
        public_id: Cloudinary public ID
        width: Optional width for resize
        height: Optional height for resize
        current_user: Current user
    
    Returns:
        Optimized URL
    """
    
    try:
        asset_service = AssetService()
        url = asset_service.get_asset_url(
            public_id=public_id,
            width=width,
            height=height
        )
        
        return {
            "success": True,
            "url": url,
            "transformations": {
                "width": width,
                "height": height
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
