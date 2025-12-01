"""
Analytics Service - Track portfolio generation usage and metrics

Logs generation events for analytics, success rates, performance metrics, etc.
"""

import time
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from models import GenerationLog, User


class AnalyticsService:
    """Track and analyze portfolio generation metrics"""
    
    async def log_generation(
        self,
        user_id: Optional[str],
        session_id: str,
        prompt: str,
        framework: str,
        success: bool,
        generation_time: float,
        file_count: int,
        error_message: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> bool:
        """
        Log a portfolio generation event.
        
        Args:
            user_id: ID of user (optional for guests)
            session_id: Portfolio session ID
            prompt: User's design prompt
            framework: Framework used (nextjs, react, etc.)
            success: Whether generation was successful
            generation_time: Time taken in seconds
            file_count: Number of files generated
            error_message: Error message if failed
            db: Database session
        
        Returns:
            True if logged successfully
        """
        
        if not db:
            return False
        
        try:
            log = GenerationLog(
                user_id=user_id,
                session_id=session_id,
                prompt=prompt,
                framework=framework,
                success=success,
                error_message=error_message,
                generation_time_seconds=generation_time,
                file_count=file_count if success else 0
            )
            
            db.add(log)
            await db.commit()
            return True
        
        except Exception as e:
            print(f"⚠️  Analytics logging error: {e}")
            return False
    
    async def get_user_stats(
        self,
        user_id: str,
        days: int = 30,
        db: Optional[AsyncSession] = None
    ) -> dict:
        """
        Get generation statistics for a user.
        
        Args:
            user_id: User ID
            days: Look back this many days
            db: Database session
        
        Returns:
            User statistics dictionary
        """
        
        if not db:
            return {}
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all logs for user in period
            result = await db.execute(
                select(GenerationLog).where(
                    (GenerationLog.user_id == user_id) &
                    (GenerationLog.created_at >= cutoff_date)
                )
            )
            logs = result.scalars().all()
            
            if not logs:
                return {
                    "user_id": user_id,
                    "period_days": days,
                    "total_generations": 0,
                    "successful": 0,
                    "failed": 0,
                    "success_rate": 0
                }
            
            successful = sum(1 for log in logs if log.success)
            failed = len(logs) - successful
            avg_time = sum(log.generation_time_seconds for log in logs) / len(logs)
            total_files = sum(log.file_count for log in logs)
            
            framework_counts = {}
            for log in logs:
                framework_counts[log.framework] = framework_counts.get(log.framework, 0) + 1
            
            return {
                "user_id": user_id,
                "period_days": days,
                "total_generations": len(logs),
                "successful": successful,
                "failed": failed,
                "success_rate": round((successful / len(logs)) * 100, 2) if logs else 0,
                "avg_generation_time_seconds": round(avg_time, 2),
                "total_files_generated": total_files,
                "frameworks_used": framework_counts,
                "date_range": {
                    "from": cutoff_date.isoformat(),
                    "to": datetime.utcnow().isoformat()
                }
            }
        
        except Exception as e:
            print(f"⚠️  Stats retrieval error: {e}")
            return {}
    
    async def get_platform_stats(
        self,
        days: int = 30,
        db: Optional[AsyncSession] = None
    ) -> dict:
        """
        Get generation statistics for entire platform.
        
        Args:
            days: Look back this many days
            db: Database session
        
        Returns:
            Platform statistics
        """
        
        if not db:
            return {}
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all logs in period
            result = await db.execute(
                select(GenerationLog).where(
                    GenerationLog.created_at >= cutoff_date
                )
            )
            logs = result.scalars().all()
            
            if not logs:
                return {
                    "period_days": days,
                    "total_generations": 0,
                    "success_rate": 0
                }
            
            successful = sum(1 for log in logs if log.success)
            failed = len(logs) - successful
            avg_time = sum(log.generation_time_seconds for log in logs) / len(logs)
            
            # Count unique users
            unique_users = len(set(log.user_id for log in logs if log.user_id))
            
            # Framework distribution
            framework_dist = {}
            for log in logs:
                framework_dist[log.framework] = framework_dist.get(log.framework, 0) + 1
            
            # Prompt analysis
            prompt_keywords = {}
            common_keywords = ["bold", "modern", "minimalist", "animated", "gradient", 
                             "dark", "light", "colorful", "professional", "creative"]
            for log in logs:
                for keyword in common_keywords:
                    if keyword.lower() in log.prompt.lower():
                        prompt_keywords[keyword] = prompt_keywords.get(keyword, 0) + 1
            
            return {
                "period_days": days,
                "total_generations": len(logs),
                "successful": successful,
                "failed": failed,
                "success_rate": round((successful / len(logs)) * 100, 2),
                "unique_users": unique_users,
                "avg_generation_time_seconds": round(avg_time, 2),
                "frameworks_used": framework_dist,
                "popular_keywords": dict(
                    sorted(prompt_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
                ),
                "daily_average": round(len(logs) / days, 2),
                "date_range": {
                    "from": cutoff_date.isoformat(),
                    "to": datetime.utcnow().isoformat()
                }
            }
        
        except Exception as e:
            print(f"⚠️  Platform stats error: {e}")
            return {}
    
    async def get_framework_stats(
        self,
        framework: str,
        days: int = 30,
        db: Optional[AsyncSession] = None
    ) -> dict:
        """
        Get statistics for a specific framework.
        
        Args:
            framework: Framework name (nextjs, react, etc.)
            days: Look back this many days
            db: Database session
        
        Returns:
            Framework statistics
        """
        
        if not db:
            return {}
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await db.execute(
                select(GenerationLog).where(
                    (GenerationLog.framework == framework) &
                    (GenerationLog.created_at >= cutoff_date)
                )
            )
            logs = result.scalars().all()
            
            if not logs:
                return {
                    "framework": framework,
                    "total_generations": 0
                }
            
            successful = sum(1 for log in logs if log.success)
            failed = len(logs) - successful
            avg_time = sum(log.generation_time_seconds for log in logs) / len(logs)
            
            return {
                "framework": framework,
                "total_generations": len(logs),
                "successful": successful,
                "failed": failed,
                "success_rate": round((successful / len(logs)) * 100, 2),
                "avg_generation_time_seconds": round(avg_time, 2),
                "total_files": sum(log.file_count for log in logs)
            }
        
        except Exception as e:
            print(f"⚠️  Framework stats error: {e}")
            return {}
    
    async def get_failed_generations(
        self,
        limit: int = 10,
        days: int = 7,
        db: Optional[AsyncSession] = None
    ) -> list:
        """
        Get recent failed generations for debugging.
        
        Args:
            limit: Max results
            days: Look back this many days
            db: Database session
        
        Returns:
            List of failed generation logs
        """
        
        if not db:
            return []
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await db.execute(
                select(GenerationLog)
                .where(
                    (GenerationLog.success == False) &
                    (GenerationLog.created_at >= cutoff_date)
                )
                .order_by(GenerationLog.created_at.desc())
                .limit(limit)
            )
            logs = result.scalars().all()
            
            return [
                {
                    "session_id": log.session_id,
                    "framework": log.framework,
                    "error": log.error_message,
                    "timestamp": log.created_at.isoformat(),
                    "prompt_preview": log.prompt[:100] + "..." if len(log.prompt) > 100 else log.prompt
                }
                for log in logs
            ]
        
        except Exception as e:
            print(f"⚠️  Failed generations retrieval error: {e}")
            return []
    
    async def get_slow_generations(
        self,
        threshold_seconds: float = 30,
        limit: int = 10,
        db: Optional[AsyncSession] = None
    ) -> list:
        """
        Get generations that took longer than threshold.
        
        Args:
            threshold_seconds: Time threshold
            limit: Max results
            db: Database session
        
        Returns:
            List of slow generation logs
        """
        
        if not db:
            return []
        
        try:
            result = await db.execute(
                select(GenerationLog)
                .where(GenerationLog.generation_time_seconds > threshold_seconds)
                .order_by(GenerationLog.generation_time_seconds.desc())
                .limit(limit)
            )
            logs = result.scalars().all()
            
            return [
                {
                    "session_id": log.session_id,
                    "framework": log.framework,
                    "time_seconds": log.generation_time_seconds,
                    "success": log.success,
                    "timestamp": log.created_at.isoformat()
                }
                for log in logs
            ]
        
        except Exception as e:
            print(f"⚠️  Slow generations retrieval error: {e}")
            return []
