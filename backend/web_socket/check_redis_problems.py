# Check connection without Redis
# Код класса для проверки каналов и соедеинения без использования Редис
# Если на фронте каждые 5 секунд будут печататься в консоли
# WebSocket message: {ping: 'pong'}, то проблема в Редис


import asyncio
import json

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

        if not token:
            logger.warning("No token provided.")
            await self.close(code=4001)
            return

        self.user = await self.get_user_from_token(token)
        if self.user is None:
            logger.error("User is None after token validation.")
            await self.close(code=4003)
            return

        self.channel_name_redis = f"user:{self.user.id}"

        await self.accept()  # ← ВАЖНО: должен быть только один вызов accept()

        # Вместо Redis подписки — просто пингуем
        async def send_pings():
            while True:
                try:
                    await self.send(text_data=json.dumps({"ping": "pong"}))
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"Error sending ping: {e}")
                    break

        self.listen_task = asyncio.create_task(send_pings())

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            from rest_framework_simplejwt.authentication import JWTAuthentication
            validated_token = JWTAuthentication().get_validated_token(token)
            user = JWTAuthentication().get_user(validated_token)
            return user
        except Exception as e:
            print(f"Token authentication failed: {e}")
            return None

    async def disconnect(self, close_code):
        if hasattr(self, "listen_task"):
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass
        logger.info(f"Disconnected with code {close_code}")



# class ProgressConsumer(AsyncWebsocketConsumer):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.listen_task = None
#         self.channel_name_redis = None
#         self.user = None
#         self.pubsub = None
#         self.redis_client = None
#
#     async def connect(self):
#         logger.info("Attempting to connect...")
#         query_string = self.scope['query_string'].decode()
#         query_params = parse_qs(query_string)
#         token = query_params.get("token", [None])[0]
#         logger.info(f"Token received: {token}")
#
#         if not token:
#             logger.warning("No token provided.")
#             await self.close(code=4001)
#             return
#
#         self.user = await self.get_user_from_token(token)
#         logger.info(f"User: {self.user}")
#
#         if self.user is None:
#             logger.error("User is None after token validation.")
#             await self.close(code=4003)
#             return
#
#         await self.accept()
#
#         try:
#             # Connect to Redis
#             self.redis_client = redis.from_url(
#                 os.getenv('REDIS_URL'), # REDIS_URL='redis://localhost:6379'
#                 health_check_interval=10,
#                 socket_connect_timeout=5,
#                 retry_on_timeout=True,
#                 socket_keepalive=True
#             )
#             #self.redis_client = redis.from_url(os.getenv('REDIS_URL'))
#
#             # Create a PubSub instance
#             self.pubsub = self.redis_client.pubsub()
#
#             # Name of special channel
#             self.channel_name_redis = f"user:{self.user.id}"
#
#             # Subscribe to channel
#             await self.pubsub.subscribe(self.channel_name_redis)
#             logger.info(f"Subscribed to Redis channel: {self.channel_name_redis}")
#
#             ######
#             def redis_auto_check(p):
#                 t = threading.Timer(5, redis_auto_check, [p])
#                 t.start()
#                 p.check_health()
#
#             redis_auto_check(self.pubsub)
#
#             # Start listening task
#             #self.listen_task = asyncio.create_task(self.listen())
#
#         except Exception as e:
#             logger.error(f"Redis connection error during subscribe: {e}")
#             await self.close(code=4004)
#
#     async def listen(self):
#         try:
#             async for message in self.pubsub.listen():
#                 if message['type'] == 'message':
#                     try:
#                         data = json.loads(message['data'])
#                         await self.send(text_data=json.dumps(data))
#                         logger.info(f"Received message from Redis: {data}")
#                     except json.JSONDecodeError:
#                         logger.warning(f"Malformed message received: {message['data']}")
#                         await self.send(text_data=json.dumps({"error": "Malformed message received"}))
#
#         except asyncio.CancelledError:
#             logger.info(f"Redis listener cancelled for Task ID {self.channel_name_redis}") # Refactor
#         except Exception as e:
#             logger.error(f"Error in message listening: {e}")
#             await self.send(text_data=json.dumps({"error": f"Error in message listening: {str(e)}"}))
#         finally:
#             pass
#             await self.pubsub.unsubscribe(f'message_channel_{self.channel_name_redis}')
#             logger.info(f"Unsubscribed from Redis channel: message_channel_{self.channel_name_redis}")
#             await self.pubsub.close()
#
#     async def disconnect(self, close_code):
#         if hasattr(self, "pubsub"):
#             await self.pubsub.unsubscribe(self.channel_name_redis)
#             await self.pubsub.close()
#         if hasattr(self, "listen_task"):
#             self.listen_task.cancel()
#             try:
#                 await self.listen_task
#             except asyncio.CancelledError:
#                 pass
#         logger.info(f"Disconnected with code {close_code}")
#
#     @database_sync_to_async
#     def get_user_from_token(self, token):
#         try:
#             from rest_framework_simplejwt.authentication import JWTAuthentication
#             validated_token = JWTAuthentication().get_validated_token(token)
#             user = JWTAuthentication().get_user(validated_token)
#             return user
#         except Exception as e:
#             print(f"Token authentication failed: {e}")
#             return None

#
#
# USE_REDIS = os.getenv('USE_REDIS', 'false').lower() == 'true'
#
# class ProgressConsumer(AsyncWebsocketConsumer):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.listen_task = None
#         self.channel_name_redis = None
#         self.user = None
#         self.pubsub = None
#         self.redis_client = None
#
#     async def connect(self):
#         logger.info("Attempting to connect...")
#         query_string = self.scope['query_string'].decode()
#         query_params = parse_qs(query_string)
#         token = query_params.get("token", [None])[0]
#         logger.info(f"Token received: {token}")
#
#         if not token:
#             logger.warning("No token provided.")
#             await self.close(code=4001)
#             return
#
#         self.user = await self.get_user_from_token(token)
#         logger.info(f"User: {self.user}")
#
#         if self.user is None:
#             logger.error("User is None after token validation.")
#             await self.close(code=4003)
#             return
#
#         await self.accept()
#
#         if USE_REDIS:
#             try:
#                 self.redis_client = redis.from_url(
#                     os.getenv('REDIS_URL'),
#                     health_check_interval=10,
#                     socket_connect_timeout=5,
#                     retry_on_timeout=True,
#                     socket_keepalive=True
#                 )
#
#                 self.pubsub = self.redis_client.pubsub()
#                 self.channel_name_redis = f"user:{self.user.id}"
#                 await asyncio.to_thread(self.pubsub.subscribe, self.channel_name_redis)
#                 logger.info(f"Subscribed to Redis channel: {self.channel_name_redis}")
#
#                 if self.pubsub:
#                     self.listen_task = asyncio.create_task(self.listen())
#
#             except Exception as e:
#                 logger.error(f"Redis connection error: {e}")
#                 self.pubsub = None
#
#     async def listen(self):
#
#         if not self.pubsub:
#                 logger.warning("No pubsub instance, skipping listen loop.")
#                 return
#
#         try:
#             while True:
#                 message = await asyncio.to_thread(self.pubsub.get_message, ignore_subscribe_messages=True, timeout=1)
#                 if message:
#                     logger.info(f"Received message: {message}")
#                     try:
#                         data = json.loads(message['data'])
#                         await self.send(text_data=json.dumps(data))
#                     except json.JSONDecodeError:
#                         logger.warning(f"Malformed message received: {message['data']}")
#                         await self.send(text_data=json.dumps({"error": "Malformed message received"}))
#                 await asyncio.sleep(0.1)
#
#         except asyncio.CancelledError:
#             logger.info("Redis listener task cancelled.")
#         except Exception as e:
#             logger.error(f"Error in Redis listen loop: {e}")
#             await self.send(text_data=json.dumps({"error": str(e)}))
#
#     async def disconnect(self, close_code):
#         if USE_REDIS and self.pubsub:
#             try:
#                 await asyncio.to_thread(self.pubsub.unsubscribe, self.channel_name_redis)
#                 self.pubsub.close()
#                 logger.info(f"Unsubscribed from Redis channel: {self.channel_name_redis}")
#             except Exception as e:
#                 logger.warning(f"Error during Redis disconnect: {e}")
#
#         if self.listen_task:
#             self.listen_task.cancel()
#             try:
#                 await self.listen_task
#             except asyncio.CancelledError:
#                 pass
#
#         logger.info(f"WebSocket disconnected with code {close_code}")
#
#     @database_sync_to_async
#     def get_user_from_token(self, token):
#         try:
#             from rest_framework_simplejwt.authentication import JWTAuthentication
#             validated_token = JWTAuthentication().get_validated_token(token)
#             user = JWTAuthentication().get_user(validated_token)
#             return user
#         except Exception as e:
#             logger.error(f"Token authentication failed: {e}")
#             return None
