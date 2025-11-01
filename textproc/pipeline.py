import asyncio
import aiostream.stream
from typing import Any, AsyncIterator, Callable, Dict, List
from importlib.metadata import entry_points
        
class Pipeline:
    """Asynchronous data processing pipeline defined by a JSON DSL."""

    def __init__(self, config):
        self.config = config
        self.compiled_steps = self._compile_pipeline(config)

    def _compile_pipeline(self, config):
        compiled = []
        available_eps = {ep.name: ep for ep in entry_points(group="textproc.filter")}

        for step in config["steps"]:
            if len(step) != 1:
                raise ValueError(f"Each step must define exactly one function: got {step}")

            func_name, kwargs = next(iter(step.items()))
            if "__ignore__" in func_name: continue
            
            ep = available_eps.get(func_name)
            if ep is None:
                raise ValueError(f"No entry point named '{func_name}' in group textproc.filter")

            compiled.append((ep.load(), kwargs))

        return compiled

    async def run(self, input_stream):
        current_stream = input_stream

        if not isinstance(current_stream, AsyncIterator):
            current_stream = aiostream.stream.iterate(current_stream)
            
        for func, kwargs in self.compiled_steps:
            current_stream = func(self, current_stream, **kwargs)

        async for item in current_stream:
            yield item
