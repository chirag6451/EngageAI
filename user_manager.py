import logging
from typing import Optional, Dict, Tuple
from database import Database

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self):
        self.db = Database()
        
    def register_user(self, email: str, password: str) -> Optional[int]:
        """Register a new user"""
        try:
            # Create user account
            user_id = self.db.create_user(email, password)
            if not user_id:
                logger.error("Failed to create user account")
                return None
                
            logger.info(f"Successfully registered user: {email}")
            return user_id
            
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return None
            
    def login(self, email: str, password: str) -> Optional[int]:
        """Login user and return user_id if successful"""
        try:
            user_id = self.db.verify_user(email, password)
            if not user_id:
                logger.error("Invalid email or password")
                return None
                
            logger.info(f"User logged in successfully: {email}")
            return user_id
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return None
            
    def update_profile(self, user_id: int, profile_data: Dict) -> bool:
        """Update user profile information"""
        try:
            success = self.db.update_user_profile(user_id, profile_data)
            if success:
                logger.info(f"Successfully updated profile for user_id: {user_id}")
            else:
                logger.error(f"Failed to update profile for user_id: {user_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return False
            
    def get_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile information"""
        try:
            profile = self.db.get_user_profile(user_id)
            if not profile:
                logger.warning(f"No profile found for user_id: {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error getting profile: {str(e)}")
            return None
            
    def get_smtp_settings(self, user_id: int) -> Optional[Dict]:
        """Get user's SMTP settings"""
        try:
            profile = self.db.get_user_profile(user_id)
            if not profile:
                return None
                
            return {
                'smtp_server': profile.get('smtp_server'),
                'smtp_port': profile.get('smtp_port'),
                'smtp_username': profile.get('smtp_username'),
                'smtp_password': profile.get('smtp_password'),
                'from_email': profile.get('from_email')
            }
            
        except Exception as e:
            logger.error(f"Error getting SMTP settings: {str(e)}")
            return None
