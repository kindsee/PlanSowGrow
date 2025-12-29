#!/usr/bin/python3
"""
WSGI entry point for PlanSowGrow Flask application.
This file is used by Apache mod_wsgi to serve the application.
"""
import sys
import os
import logging

# Configure logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# Add the application directory to the Python path
sys.path.insert(0, '/home/jmgalaminos/PlanSowGrow')

# Change to the application directory
os.chdir('/home/jmgalaminos/PlanSowGrow')

# Set Flask environment
os.environ['FLASK_ENV'] = 'production'

# Import and configure the application
try:
    from app import create_app
    application = create_app('production')
    logging.info("PlanSowGrow WSGI application loaded successfully")
except Exception as e:
    logging.error(f"Error loading PlanSowGrow application: {str(e)}")
    raise
