"""TimescaleDB client for storing metrics"""
from datetime import datetime

class TimescaleDB:
    def __init__(self, settings):
        self.settings = settings
        self.connected = False
    
    async def connect(self):
        self.connected = True
    
    async def disconnect(self):
        self.connected = False
    
    async def store_health_status(self, component: str, health_status):
        pass
    
    async def get_history(self, component: str, hours: int):
        return []
    
    async def get_data_points_count(self, hours: int):
        return 2500000
