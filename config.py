#!/usr/bin/env python3
"""
Configuration Manager for IT Support Service Desk
Handles configuration loading and validation
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Application configuration management"""
    
    # Load environment variables
    load_dotenv()
    
    # Flask Configuration
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/tickets/tickets.db')
    REPORT_OUTPUT_PATH = os.getenv('REPORT_OUTPUT_PATH', 'data/reports')
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.office365.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    O365_EMAIL = os.getenv('O365_EMAIL', '')
    O365_PASSWORD = os.getenv('O365_PASSWORD', '')
    EMAIL_ENABLED = os.getenv('NOTIFICATION_ENABLED', 'True') == 'True'
    
    # Support Teams Configuration
    SUPPORT_TEAMS_CONFIG = {
        'network_support': {
            'name': 'Network Support',
            'email': os.getenv('NETWORK_SUPPORT_EMAIL', 'network-support@company.com'),
            'response_sla': 2,  # hours
            'resolution_sla': 8,  # hours
        },
        'email_support': {
            'name': 'Email & Collaboration',
            'email': os.getenv('EMAIL_SUPPORT_EMAIL', 'email-support@company.com'),
            'response_sla': 2,
            'resolution_sla': 8,
        },
        'access_support': {
            'name': 'Access & Security',
            'email': os.getenv('ACCESS_SUPPORT_EMAIL', 'access-support@company.com'),
            'response_sla': 1,
            'resolution_sla': 4,
        },
        'hardware_support': {
            'name': 'Hardware Support',
            'email': os.getenv('HARDWARE_SUPPORT_EMAIL', 'hardware-support@company.com'),
            'response_sla': 4,
            'resolution_sla': 24,
        },
        'software_support': {
            'name': 'Software Support',
            'email': os.getenv('SOFTWARE_SUPPORT_EMAIL', 'software-support@company.com'),
            'response_sla': 4,
            'resolution_sla': 24,
        },
    }
    
    # Admin Configuration
    ADMIN_USERS = {
        'admin': os.getenv('ADMIN_PASSWORD', 'admin123'),
        'support_manager': os.getenv('MANAGER_PASSWORD', 'manager123'),
    }
    
    # Application Settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_FILE_TYPES = ['pdf', 'doc', 'docx', 'xlsx', 'xls', 'txt', 'jpg', 'png']
    
    # Spelling Correction Settings
    SPELLING_CORRECTION_THRESHOLD = 0.85  # Fuzzy match threshold
    AUTO_CATEGORIZE = True
    AUTO_ASSIGN_PRIORITY = True
    
    # Ticket Settings
    DEFAULT_PRIORITY = 'P3 - Medium'
    DEFAULT_CATEGORY = 'General'
    TICKET_ID_PREFIX = 'TKT'
    AUTO_ESCALATION_ENABLED = True
    ESCALATION_HOURS = 8
    
    # UI Settings
    ITEMS_PER_PAGE = 25
    MAX_SEARCH_RESULTS = 100
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/service-desk.log')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # Ensure sensitive values are set in production
    if not Config.SECRET_KEY or Config.SECRET_KEY == 'dev-key-change-in-production':
        raise ValueError('SECRET_KEY must be configured for production')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_PATH = ':memory:'  # Use in-memory database for tests
    EMAIL_ENABLED = False


def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)


def load_custom_config(config_file):
    """Load custom configuration from JSON file"""
    if not os.path.exists(config_file):
        return {}
    
    with open(config_file, 'r') as f:
        return json.load(f)


def validate_config(config):
    """Validate configuration"""
    required_dirs = [
        config.DATABASE_PATH.rsplit('/', 1)[0],
        config.REPORT_OUTPUT_PATH,
        config.LOG_FILE.rsplit('/', 1)[0] if config.LOG_FILE else None,
    ]
    
    for dir_path in required_dirs:
        if dir_path:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    return True


if __name__ == '__main__':
    # Test configuration
    config = get_config()
    print("Current Configuration:")
    print(f"  Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"  Debug Mode: {config.DEBUG}")
    print(f"  Database: {config.DATABASE_PATH}")
    print(f"  Reports: {config.REPORT_OUTPUT_PATH}")
    print(f"  Email Enabled: {config.EMAIL_ENABLED}")
    print(f"  Spelling Correction: {config.AUTO_CATEGORIZE}")
    print("\nConfiguration loaded successfully!")
