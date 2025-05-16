import asyncio
import json
import os

import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

from dotenv import load_dotenv
load_dotenv()

import logging
logger = logging.getLogger(__name__)

class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("Attempting to connect...")
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]
        logger.info(f"Token received: {token}")

        self.user = await self.get_user_from_token(token)

        if not self.user:
            logger.warning("Authentication failed. Closing connection.")
            await self.close()
            return

        self.channel_name_redis = f"user:{self.user.id}"

        try:
            self.redis = redis.from_url(
                os.getenv('REDIS_URL', 'redis://localhost:6379'),
                health_check_interval=10,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                socket_keepalive=True
            )
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            await self.close()
            return

        await self.accept()
        logger.info(f"WebSocket accepted for user {self.user.id}")
        asyncio.create_task(self.listen_redis())

    async def listen_redis(self):
        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(self.channel_name_redis)
            async for message in pubsub.listen():
                if message["type"] == "message":
                    logger.info(f"Sending message to frontend: {message['data']}")
                    await self.send(message["data"])
        except Exception as e:
            logger.error(f"Error listening to Redis: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.redis.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.warning(f"Error during disconnect: {e}")

    @database_sync_to_async
    def get_user_from_token(self, token):
        from rest_framework_simplejwt.authentication import JWTAuthentication
        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            return user
        except Exception as e:
            logger.warning(f"Token authentication failed: {e}")
            return None