"""
Database connection and operations using Supabase.
"""

import asyncio
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from datetime import datetime
import json
import logging

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global Supabase client
supabase_client: Optional[Client] = None


async def init_db():
    """Initialize database connection."""
    global supabase_client
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        logger.warning("Supabase credentials not configured. Database features will be limited.")
        return
    
    try:
        supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("✅ Database connection initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


def get_db() -> Optional[Client]:
    """Get database client."""
    return supabase_client


class DatabaseManager:
    """Database operations manager."""
    
    def __init__(self):
        self.client = get_db()
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        if not self.client:
            raise Exception("Database not initialized")
        
        try:
            result = self.client.table('users').insert(user_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        if not self.client:
            return None
        
        try:
            result = self.client.table('users').select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    async def save_omr_result(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save OMR processing result."""
        if not self.client:
            # If no database, return the data as-is for local storage
            return result_data
        
        try:
            # Prepare data for database
            db_data = {
                'user_id': result_data.get('user_id'),
                'filename': result_data.get('filename'),
                'student_info': json.dumps(result_data.get('student_info', {})),
                'answers': json.dumps(result_data.get('answers', {})),
                'scores': json.dumps(result_data.get('scores', {})),
                'total_score': result_data.get('total_score', 0),
                'confidence_score': result_data.get('confidence_score', 0),
                'processing_time': result_data.get('processing_time', 0),
                'created_at': datetime.utcnow().isoformat(),
                'metadata': json.dumps(result_data.get('metadata', {}))
            }
            
            result = self.client.table('omr_results').insert(db_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error saving OMR result: {e}")
            raise
    
    async def get_user_results(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get OMR results for a user."""
        if not self.client:
            return []
        
        try:
            result = self.client.table('omr_results')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            # Parse JSON fields
            for item in result.data:
                item['student_info'] = json.loads(item.get('student_info', '{}'))
                item['answers'] = json.loads(item.get('answers', '{}'))
                item['scores'] = json.loads(item.get('scores', '{}'))
                item['metadata'] = json.loads(item.get('metadata', '{}'))
            
            return result.data
        except Exception as e:
            logger.error(f"Error fetching user results: {e}")
            return []
    
    async def get_result_by_id(self, result_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get specific OMR result by ID."""
        if not self.client:
            return None
        
        try:
            query = self.client.table('omr_results').select('*').eq('id', result_id)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            result = query.execute()
            
            if result.data:
                item = result.data[0]
                # Parse JSON fields
                item['student_info'] = json.loads(item.get('student_info', '{}'))
                item['answers'] = json.loads(item.get('answers', '{}'))
                item['scores'] = json.loads(item.get('scores', '{}'))
                item['metadata'] = json.loads(item.get('metadata', '{}'))
                return item
            
            return None
        except Exception as e:
            logger.error(f"Error fetching result: {e}")
            return None
    
    async def delete_result(self, result_id: str, user_id: str) -> bool:
        """Delete an OMR result."""
        if not self.client:
            return False
        
        try:
            result = self.client.table('omr_results')\
                .delete()\
                .eq('id', result_id)\
                .eq('user_id', user_id)\
                .execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting result: {e}")
            return False
    
    async def get_processing_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get processing statistics."""
        if not self.client:
            return {
                'total_processed': 0,
                'average_score': 0,
                'average_confidence': 0,
                'processing_time_avg': 0
            }
        
        try:
            query = self.client.table('omr_results').select('total_score,confidence_score,processing_time')
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            result = query.execute()
            
            if not result.data:
                return {
                    'total_processed': 0,
                    'average_score': 0,
                    'average_confidence': 0,
                    'processing_time_avg': 0
                }
            
            data = result.data
            total_count = len(data)
            avg_score = sum(item.get('total_score', 0) for item in data) / total_count
            avg_confidence = sum(item.get('confidence_score', 0) for item in data) / total_count
            avg_processing_time = sum(item.get('processing_time', 0) for item in data) / total_count
            
            return {
                'total_processed': total_count,
                'average_score': round(avg_score, 2),
                'average_confidence': round(avg_confidence, 3),
                'processing_time_avg': round(avg_processing_time, 2)
            }
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return {
                'total_processed': 0,
                'average_score': 0,
                'average_confidence': 0,
                'processing_time_avg': 0
            }


# Global database manager instance
db_manager = DatabaseManager()