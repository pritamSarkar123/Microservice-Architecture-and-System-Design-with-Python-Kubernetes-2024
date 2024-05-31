import time
from functools import wraps

import redis
from fastapi import HTTPException

from ..config import settings

if settings.redis_password:
    connection_pool = redis.ConnectionPool(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
        password=settings.redis_password,
    )
else:
    connection_pool = redis.ConnectionPool(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
    )


async def get_redis_connection():
    return redis.StrictRedis(connection_pool=connection_pool)


def rate_limiter(max_requests: int = 10, period: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if request:
                client_ip = request.client.host
                redis_conn = await get_redis_connection()
                key = f"rate_limit:{client_ip}"
                current_time = int(time.time())
                window_start = current_time - period

                requests_in_window = redis_conn.zrangebyscore(
                    key, window_start, current_time
                )
                num_requests = len(requests_in_window)

                if num_requests >= max_requests:
                    raise HTTPException(status_code=429, detail="Too many requests")

                redis_conn.zadd(key, {current_time: current_time})
                redis_conn.expire(
                    key, period + 1
                )  # Set an expiry slightly longer than the window

            return await func(*args, **kwargs)

        return wrapper

    return decorator
