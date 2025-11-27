import time
import json
import os
from collections import deque
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger("GeminiProxy")

try:
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

class KeyManager:
    def __init__(self, key_file="list_api.txt", usage_file="usage_log.json"):
        self.key_file = key_file
        self.keys = self._load_keys()
        self.lock = asyncio.Lock()
        
        # Firestore setup
        self.use_firestore = False
        self.db = None
        
        firebase_creds = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        if FIREBASE_AVAILABLE and firebase_creds:
            try:
                # Parse the JSON string from env var
                cred_dict = json.loads(firebase_creds)
                cred = credentials.Certificate(cred_dict)
                # Check if app is already initialized to avoid errors on reload
                if not firebase_admin._apps:
                    firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.use_firestore = True
                logger.info("Firestore initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Firestore: {e}")
                # Fallback to file
        
        if not self.use_firestore:
            # Check if we are in a read-only environment (like Vercel)
            # If so, use /tmp for the usage file
            if os.access(".", os.W_OK):
                self.usage_file = usage_file
            else:
                self.usage_file = "/tmp/usage_log.json"
            logger.info(f"Using local file storage: {self.usage_file}")

        self.usage_data = self._load_usage()

    def _load_keys(self):
        try:
            with open(self.key_file, "r") as f:
                # Filter out empty lines and strip whitespace
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Warning: {self.key_file} not found.")
            return []

    def _load_usage(self):
        if self.use_firestore:
            try:
                doc = self.db.collection('api_usage').document('gemini_proxy').get()
                if doc.exists:
                    return doc.to_dict()
                return {}
            except Exception as e:
                logger.error(f"Error loading from Firestore: {e}")
                return {}
        else:
            if os.path.exists(self.usage_file):
                try:
                    with open(self.usage_file, "r") as f:
                        data = json.load(f)
                        return data
                except json.JSONDecodeError:
                    return {}
            return {}

    def _save_usage(self):
        if self.use_firestore:
            try:
                # Use set with merge=True or just overwrite? 
                # Overwrite is safer for the whole dict structure we maintain
                self.db.collection('api_usage').document('gemini_proxy').set(self.usage_data)
            except Exception as e:
                logger.error(f"Error saving to Firestore: {e}")
        else:
            try:
                with open(self.usage_file, "w") as f:
                    json.dump(self.usage_data, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving to file: {e}")

    def _cleanup_old_usage(self, key):
        """Removes usage records older than 24 hours for daily limit and 1 minute for minute limit."""
        if key not in self.usage_data:
            self.usage_data[key] = []
        
        now = time.time()
        one_day_ago = now - 86400
        
        # Keep only timestamps within the last 24 hours
        self.usage_data[key] = [t for t in self.usage_data[key] if t > one_day_ago]

    def _is_rate_limited(self, key):
        self._cleanup_old_usage(key)
        timestamps = self.usage_data[key]
        now = time.time()
        
        # Check minute limit: Max 2 requests per minute
        one_minute_ago = now - 60
        requests_last_minute = sum(1 for t in timestamps if t > one_minute_ago)
        if requests_last_minute >= 2:
            return True, "Minute limit reached"

        # Check daily limit: Max 50 requests per day
        # (Already cleaned up to last 24 hours)
        if len(timestamps) >= 50:
            return True, "Daily limit reached"

        return False, None

    async def get_available_key(self):
        async with self.lock:
            if self.use_firestore:
                 self.usage_data = self._load_usage()

            for key in self.keys:
                is_limited, reason = self._is_rate_limited(key)
                if not is_limited:
                    return key
            
            return None

    async def record_usage(self, key):
        async with self.lock:
            if key not in self.usage_data:
                self.usage_data[key] = []
            self.usage_data[key].append(time.time())
            self._save_usage()

    def get_key_stats(self):
        stats = {}
        for key in self.keys:
            self._cleanup_old_usage(key)
            timestamps = self.usage_data.get(key, [])
            now = time.time()
            one_minute_ago = now - 60
            req_last_min = sum(1 for t in timestamps if t > one_minute_ago)
            stats[key] = {
                "total_last_24h": len(timestamps),
                "last_minute": req_last_min
            }
        return stats
