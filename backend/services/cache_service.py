"""
Cache Service - Redis-based caching for portfolios

Caches generated portfolios to avoid regenerating identical portfolios.
Uses Redis for fast in-memory storage with TTL support.
"""

import os
import json
import hashlib
import redis
from typing import Optional, Dict
from datetime import datetime


class CacheService:
    """Cache generated portfolios using Redis"""
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_password = os.getenv("REDIS_PASSWORD", None)
            redis_db = int(os.getenv("REDIS_DB", 0))
            
            # Configure SSL for cloud Redis
            use_ssl = redis_host != "localhost"
            ssl_params = {}
            if use_ssl:
                import ssl
                ssl_params = {
                    "ssl": True,
                    "ssl_cert_reqs": ssl.CERT_NONE  # Disable certificate verification
                }
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                **ssl_params
            )
            # Test connection
            self.redis_client.ping()
            self.configured = True
            print(f"✅ Redis connected: {redis_host}:{redis_port}")
        except Exception as e:
            print(f"⚠️  Redis not available: {e}")
            self.redis_client = None
            self.configured = False
    
    def _get_cache_key(self, prompt: str, resume_data: Dict, framework: str) -> str:
        """
        Generate cache key from prompt, resume, and framework.
        
        Args:
            prompt: User's design prompt
            resume_data: Resume data dictionary
            framework: Framework (nextjs, react, etc.)
        
        Returns:
            SHA256 hash for use as cache key
        """
        
        # Create deterministic cache key from inputs
        cache_input = {
            "prompt": prompt.lower().strip(),
            "resume": json.dumps(resume_data, sort_keys=True),
            "framework": framework
        }
        
        cache_str = json.dumps(cache_input, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def get_cached_portfolio(
        self,
        prompt: str,
        resume_data: Dict,
        framework: str = "nextjs"
    ) -> Optional[Dict]:
        """
        Get cached portfolio if available.
        
        Args:
            prompt: Design prompt
            resume_data: Resume data
            framework: Target framework
        
        Returns:
            Cached portfolio or None if not found
        """
        
        if not self.configured:
            return None
        
        try:
            cache_key = self._get_cache_key(prompt, resume_data, framework)
            cached = self.redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            return None
        
        except Exception as e:
            print(f"⚠️  Cache retrieval error: {e}")
            return None
    
    def cache_portfolio(
        self,
        prompt: str,
        resume_data: Dict,
        portfolio: Dict,
        framework: str = "nextjs",
        ttl: int = 3600
    ) -> bool:
        """
        Cache generated portfolio.
        
        Args:
            prompt: Design prompt
            resume_data: Resume data
            portfolio: Generated portfolio data
            framework: Target framework
            ttl: Time to live in seconds (default 1 hour)
        
        Returns:
            True if cached successfully
        """
        
        if not self.configured:
            return False
        
        try:
            cache_key = self._get_cache_key(prompt, resume_data, framework)
            cache_data = {
                "portfolio": portfolio,
                "cached_at": datetime.now().isoformat(),
                "framework": framework
            }
            
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            return True
        
        except Exception as e:
            print(f"⚠️  Cache storage error: {e}")
            return False
    
    def cache_variation(
        self,
        prompt: str,
        resume_data: Dict,
        variation_number: int,
        portfolio: Dict,
        ttl: int = 3600
    ) -> bool:
        """
        Cache portfolio variation separately.
        
        Args:
            prompt: Base design prompt
            resume_data: Resume data
            variation_number: Variation number (1-5)
            portfolio: Generated variation
            ttl: Time to live
        
        Returns:
            True if cached successfully
        """
        
        if not self.configured:
            return False
        
        try:
            base_key = self._get_cache_key(prompt, resume_data, "nextjs")
            variation_key = f"{base_key}:variation_{variation_number}"
            
            self.redis_client.setex(
                variation_key,
                ttl,
                json.dumps(portfolio)
            )
            return True
        
        except Exception as e:
            print(f"⚠️  Variation cache error: {e}")
            return False
    
    def get_variation(
        self,
        prompt: str,
        resume_data: Dict,
        variation_number: int
    ) -> Optional[Dict]:
        """
        Get cached portfolio variation.
        
        Args:
            prompt: Design prompt
            resume_data: Resume data
            variation_number: Variation number
        
        Returns:
            Cached variation or None
        """
        
        if not self.configured:
            return None
        
        try:
            base_key = self._get_cache_key(prompt, resume_data, "nextjs")
            variation_key = f"{base_key}:variation_{variation_number}"
            
            cached = self.redis_client.get(variation_key)
            if cached:
                return json.loads(cached)
            return None
        
        except Exception as e:
            print(f"⚠️  Variation retrieval error: {e}")
            return None
    
    def invalidate_cache(
        self,
        prompt: str,
        resume_data: Dict,
        framework: str = "nextjs"
    ) -> bool:
        """
        Invalidate/delete cached portfolio.
        
        Args:
            prompt: Design prompt
            resume_data: Resume data
            framework: Target framework
        
        Returns:
            True if deleted successfully
        """
        
        if not self.configured:
            return False
        
        try:
            cache_key = self._get_cache_key(prompt, resume_data, framework)
            self.redis_client.delete(cache_key)
            return True
        
        except Exception as e:
            print(f"⚠️  Cache invalidation error: {e}")
            return False
    
    def clear_all_cache(self) -> bool:
        """Clear all cached portfolios (use with caution)"""
        
        if not self.configured:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"⚠️  Cache clear error: {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        
        if not self.configured:
            return {
                "configured": False,
                "message": "Redis not available"
            }
        
        try:
            info = self.redis_client.info()
            return {
                "configured": True,
                "used_memory": info.get("used_memory_human"),
                "total_commands_processed": info.get("total_commands_processed"),
                "connected_clients": info.get("connected_clients")
            }
        except Exception as e:
            return {
                "configured": False,
                "error": str(e)
            }
