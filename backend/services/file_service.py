"""
File Service - Handle file downloads and ZIP creation

Manages portfolio file downloads, ZIP archive creation, and temporary storage.
"""

import os
import zipfile
import io
import json
import tempfile
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime


class FileService:
    """Handle file downloads and ZIP creation for generated portfolios"""
    
    def __init__(self):
        """Initialize file service with temp directory"""
        self.temp_dir = Path("temp_downloads")
        self.temp_dir.mkdir(exist_ok=True)
    
    def create_project_zip(self, files: Dict[str, str], project_name: str) -> bytes:
        """
        Create ZIP archive from generated portfolio files.
        
        Args:
            files: Dictionary of filepath -> content
            project_name: Name for the project (used in folder structure)
        
        Returns:
            Bytes of ZIP file
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Create root folder with project name
            root_folder = project_name.replace(" ", "_").replace("'", "")
            
            for filepath, content in files.items():
                # Handle JSON objects (like package.json)
                if isinstance(content, dict):
                    content = json.dumps(content, indent=2)
                
                # Add file to ZIP with root folder
                full_path = f"{root_folder}/{filepath}"
                zip_file.writestr(full_path, content)
        
        # Reset buffer position to beginning
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def get_zip_filename(self, project_name: str, session_id: str) -> str:
        """Generate filename for ZIP archive"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = project_name.replace(" ", "_").replace("'", "")[:30]
        return f"portfolio_{safe_name}_{session_id[:8]}_{timestamp}.zip"
    
    async def save_zip_temp(
        self,
        files: Dict[str, str],
        project_name: str,
        session_id: str
    ) -> str:
        """
        Save ZIP to temporary file and return path.
        
        Args:
            files: Dictionary of files
            project_name: Project name
            session_id: Session ID
        
        Returns:
            Path to temporary ZIP file
        """
        zip_data = self.create_project_zip(files, project_name)
        filename = self.get_zip_filename(project_name, session_id)
        filepath = self.temp_dir / filename
        
        # Write ZIP file synchronously
        with open(filepath, 'wb') as f:
            f.write(zip_data)
        
        return str(filepath)
    
    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up temporary ZIP files older than max_age_hours.
        
        Args:
            max_age_hours: Remove files older than this many hours
        
        Returns:
            Number of files deleted
        """
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        
        for filepath in self.temp_dir.glob("*.zip"):
            file_age = current_time - filepath.stat().st_mtime
            
            if file_age > max_age_seconds:
                try:
                    filepath.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {filepath}: {e}")
        
        return deleted_count
    
    def get_project_structure_summary(self, files: Dict[str, str]) -> Dict:
        """
        Generate summary of project structure.
        
        Args:
            files: Dictionary of files in project
        
        Returns:
            Dictionary with file counts and structure info
        """
        file_types = {}
        total_size = 0
        
        for filepath, content in files.items():
            # Get file extension
            if '.' in filepath:
                ext = filepath.split('.')[-1]
            else:
                ext = 'no-extension'
            
            file_types[ext] = file_types.get(ext, 0) + 1
            
            # Calculate size
            if isinstance(content, dict):
                content = json.dumps(content)
            total_size += len(content.encode('utf-8'))
        
        return {
            "total_files": len(files),
            "total_size_bytes": total_size,
            "file_types": file_types,
            "size_mb": round(total_size / (1024 * 1024), 2)
        }
    
    async def validate_project_files(self, files: Dict[str, str]) -> Dict:
        """
        Validate project files for completeness.
        
        Args:
            files: Dictionary of project files
        
        Returns:
            Validation result with missing critical files
        """
        required_files = [
            "package.json",
            "app/page.tsx" or "app/page.jsx",
            "app/layout.tsx" or "app/layout.jsx",
        ]
        
        missing_files = []
        
        for required in required_files:
            # Check if file or variant exists
            if required.endswith("or"):
                continue
            
            alternatives = [f for f in files.keys() if f.endswith(required.split('/')[-1])]
            if not alternatives:
                missing_files.append(required)
        
        return {
            "is_valid": len(missing_files) == 0,
            "missing_files": missing_files,
            "warnings": []
        }
