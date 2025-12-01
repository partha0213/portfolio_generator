"""
Deployment Service - Deploy portfolios to hosting platforms

Supports Vercel and Netlify deployments. Handles API integration and deployment tracking.
"""

import os
import json
import requests
from typing import Dict, Optional
from datetime import datetime


class DeploymentService:
    """Deploy portfolios to Vercel and Netlify"""
    
    def __init__(self):
        """Initialize with platform tokens"""
        self.vercel_token = os.getenv("VERCEL_TOKEN")
        self.netlify_token = os.getenv("NETLIFY_TOKEN")
        self.vercel_api_url = "https://api.vercel.com/v13"
        self.netlify_api_url = "https://api.netlify.com/api/v1"
    
    async def deploy_to_vercel(
        self,
        files: Dict[str, str],
        project_name: str,
        session_id: str
    ) -> Dict:
        """
        Deploy portfolio to Vercel using the raw deployments endpoint.
        
        Args:
            files: Dictionary of project files
            project_name: Name for the project
            session_id: Session ID for tracking
        
        Returns:
            Deployment result with URL and status
        """
        
        if not self.vercel_token:
            return {
                "success": False,
                "error": "Vercel token not configured. Set VERCEL_TOKEN in .env",
                "platform": "vercel"
            }
        
        try:
            # Prepare file content for Vercel (as array, not dict)
            files_array = []
            for filepath, content in files.items():
                # Convert dict to JSON string if needed
                if isinstance(content, dict):
                    content = json.dumps(content, indent=2)
                
                files_array.append({
                    "file": filepath,
                    "data": content
                })
            
            # Create project name
            safe_project_name = project_name.lower().replace(" ", "-").replace("'", "")[:32]
            
            # Use Vercel deployments endpoint with files as array
            payload = {
                "name": safe_project_name,
                "files": files_array,
                "projectSettings": {
                    "framework": "nextjs"
                }
            }
            
            # Make deployment request
            headers = {
                "Authorization": f"Bearer {self.vercel_token}",
                "Content-Type": "application/json"
            }
            
            print(f"📤 Deploying {len(files_array)} files to Vercel as '{safe_project_name}'...")
            
            response = requests.post(
                f"{self.vercel_api_url}/deployments",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            print(f"Vercel API Response: {response.status_code}")
            print(f"Response body: {response.text[:500]}")  # First 500 chars for debugging
            
            if response.status_code in [200, 201]:
                data = response.json()
                deployment_url = data.get("url") or data.get("inspectorUrl")
                if deployment_url and not deployment_url.startswith("http"):
                    deployment_url = f"https://{deployment_url}"
                
                return {
                    "success": True,
                    "platform": "vercel",
                    "deployment_id": data.get("id"),
                    "url": deployment_url,
                    "status": data.get("state", "building"),
                    "created_at": datetime.now().isoformat()
                }
            else:
                # Better error reporting
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", f"Vercel API error: {response.status_code}")
                except:
                    error_msg = f"Vercel API error: {response.status_code} - {response.text[:200]}"
                
                return {
                    "success": False,
                    "error": error_msg,
                    "platform": "vercel",
                    "details": response.text
                }
        
        except Exception as e:
            print(f"Exception during Vercel deployment: {str(e)}")
            return {
                "success": False,
                "error": f"Deployment error: {str(e)}",
                "platform": "vercel"
            }

    
    async def deploy_to_netlify(
        self,
        files: Dict[str, str],
        project_name: str,
        session_id: str
    ) -> Dict:
        """
        Deploy portfolio to Netlify.
        
        Args:
            files: Dictionary of project files
            project_name: Name for the project
            session_id: Session ID for tracking
        
        Returns:
            Deployment result with URL and status
        """
        
        if not self.netlify_token:
            return {
                "success": False,
                "error": "Netlify token not configured. Set NETLIFY_TOKEN in .env",
                "platform": "netlify"
            }
        
        try:
            # Netlify requires files in different format
            file_manifest = {}
            for filepath, content in files.items():
                if isinstance(content, dict):
                    content = json.dumps(content, indent=2)
                
                file_manifest[filepath] = {
                    "data": content
                }
            
            # Create site payload
            site_payload = {
                "name": project_name.lower().replace(" ", "-").replace("'", "")[:32]
            }
            
            # First create site
            headers = {
                "Authorization": f"Bearer {self.netlify_token}",
                "Content-Type": "application/json"
            }
            
            create_response = requests.post(
                f"{self.netlify_api_url}/sites",
                headers=headers,
                json=site_payload,
                timeout=30
            )
            
            if create_response.status_code != 201:
                return {
                    "success": False,
                    "error": f"Failed to create Netlify site: {create_response.status_code}",
                    "platform": "netlify"
                }
            
            site_data = create_response.json()
            site_id = site_data.get("id")
            
            # Upload files
            upload_response = requests.post(
                f"{self.netlify_api_url}/sites/{site_id}/files",
                headers=headers,
                json=file_manifest,
                timeout=60
            )
            
            if upload_response.status_code in [200, 201]:
                return {
                    "success": True,
                    "platform": "netlify",
                    "site_id": site_id,
                    "url": site_data.get("url"),
                    "status": "deploying",
                    "created_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to upload files: {upload_response.status_code}",
                    "platform": "netlify"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "netlify"
            }
    
    async def get_deployment_status(
        self,
        platform: str,
        deployment_id: str
    ) -> Dict:
        """
        Check deployment status.
        
        Args:
            platform: "vercel" or "netlify"
            deployment_id: Deployment ID to check
        
        Returns:
            Current deployment status
        """
        
        if platform == "vercel":
            if not self.vercel_token:
                return {"success": False, "error": "Vercel token not configured"}
            
            try:
                headers = {"Authorization": f"Bearer {self.vercel_token}"}
                response = requests.get(
                    f"{self.vercel_api_url}/deployments/{deployment_id}",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "status": data.get("state"),
                        "url": f"https://{data.get('url', '')}",
                        "created_at": data.get("createdAt")
                    }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif platform == "netlify":
            if not self.netlify_token:
                return {"success": False, "error": "Netlify token not configured"}
            
            try:
                headers = {"Authorization": f"Bearer {self.netlify_token}"}
                response = requests.get(
                    f"{self.netlify_api_url}/deploys/{deployment_id}",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "status": data.get("state"),
                        "url": data.get("ssl_url") or data.get("url"),
                        "created_at": data.get("created_at")
                    }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Invalid platform"}
    
    def get_supported_platforms(self) -> Dict:
        """Return list of supported deployment platforms"""
        return {
            "platforms": [
                {
                    "name": "Vercel",
                    "id": "vercel",
                    "configured": bool(self.vercel_token),
                    "features": ["auto-scaling", "serverless", "edge-functions"]
                },
                {
                    "name": "Netlify",
                    "id": "netlify",
                    "configured": bool(self.netlify_token),
                    "features": ["build-on-push", "edge-functions", "lambda-functions"]
                }
            ]
        }
