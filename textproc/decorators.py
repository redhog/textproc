from functools import wraps
from aiostream import stream

def map(func):
    @wraps(func)
    def wrapper(pipeline, async_iter, **kwargs):
        async def item_wrapper(item):
            return await func(pipeline, item, **kwargs)
        return stream.map(
            async_iter,
            item_wrapper,
            task_limit=pipeline.config.get("task_limit", 5))
    return wrapper
