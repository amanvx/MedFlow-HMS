from functools import wraps
from flask import current_app
import json
import redis
from datetime import timedelta

# Redis client
redis_client = None


def get_redis_client():
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host="localhost", port=6379, db=0, decode_responses=True
            )
        except:
            return None
    return redis_client


def cache_key(prefix, *args):
    
    key = prefix
    for arg in args:
        key += f":{arg}"
    return key


def cached(prefix, ttl=300):
    

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                r = get_redis_client()
                if r is None:
                    return f(*args, **kwargs)

                # Generate cache key
                cache_k = cache_key(prefix, *args)

                # Try to get from cache
                cached_value = r.get(cache_k)
                if cached_value:
                    return json.loads(cached_value)

                # Call function and cache result
                result = f(*args, **kwargs)
                r.setex(cache_k, timedelta(seconds=ttl), json.dumps(result))
                return result
            except:
                # If Redis fails, just call the function
                return f(*args, **kwargs)

        return decorated_function

    return decorator


def invalidate_cache(prefix, *args):
    
    try:
        r = get_redis_client()
        if r:
            pattern = f"{prefix}:*"
            keys = r.keys(pattern)
            if keys:
                r.delete(*keys)
    except:
        pass


def cache_doctor_availability(doctor_id, availability, ttl=1800):
    
    try:
        r = get_redis_client()
        if r:
            key = f"doctor_availability:{doctor_id}"
            r.setex(key, timedelta(seconds=ttl), json.dumps(availability))
    except:
        pass


def get_cached_doctor_availability(doctor_id):
    
    try:
        r = get_redis_client()
        if r:
            key = f"doctor_availability:{doctor_id}"
            data = r.get(key)
            if data:
                return json.loads(data)
    except:
        pass
    return None


def cache_departments(departments, ttl=86400):
    
    try:
        r = get_redis_client()
        if r:
            r.setex("departments:list", timedelta(seconds=ttl), json.dumps(departments))
    except:
        pass


def get_cached_departments():
    
    try:
        r = get_redis_client()
        if r:
            data = r.get("departments:list")
            if data:
                return json.loads(data)
    except:
        pass
    return None

