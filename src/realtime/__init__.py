"""
Realtime Data Module
====================

This module handles real-time data collection and processing for pumping stations.

Functions:
    - poll_gemaal: Poll real-time pumping station data
    - generate_status: Generate status reports
    - update_dynamic: Update dynamic data
    - fetch_hydronet: Fetch data from Hydronet API
"""

from .poll_gemaal import *
from .generate_status import *
from .update_dynamic import *
from .fetch_hydronet import *
