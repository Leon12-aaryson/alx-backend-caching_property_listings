from django.core.cache import cache
from .models import Property


def get_all_properties():
    """
    Get all properties with Redis caching.
    Cache expires after 1 hour (3600 seconds).
    """
    # Try to get from cache first
    cached_properties = cache.get('all_properties')
    
    if cached_properties is not None:
        return cached_properties
    
    # If not in cache, fetch from database
    properties = Property.objects.all()
    
    # Store in cache for 1 hour
    cache.set('all_properties', properties, 3600)
    
    return properties


def get_redis_cache_metrics():
    """
    Get Redis cache hit/miss metrics.
    Returns a dictionary with cache statistics.
    """
    try:
        # Get Redis connection from django-redis
        from django_redis import get_redis_connection
        redis_client = get_redis_connection("default")
        
        # Get Redis INFO
        info = redis_client.info()
        
        # Extract cache statistics
        keyspace_hits = info.get('keyspace_hits', 0)
        keyspace_misses = info.get('keyspace_misses', 0)
        
        # Calculate hit ratio
        total_requests = keyspace_hits + keyspace_misses
        hit_ratio = keyspace_hits / total_requests if total_requests > 0 else 0
        
        metrics = {
            'keyspace_hits': keyspace_hits,
            'keyspace_misses': keyspace_misses,
            'total_requests': total_requests,
            'hit_ratio': round(hit_ratio, 4),
            'miss_ratio': round(1 - hit_ratio, 4)
        }
        
        # Log metrics
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Redis Cache Metrics: {metrics}")
        
        return metrics
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting Redis cache metrics: {e}")
        
        return {
            'error': str(e),
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'total_requests': 0,
            'hit_ratio': 0,
            'miss_ratio': 0
        }
