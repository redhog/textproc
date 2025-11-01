from .. import pipeline as pipelinemod
from .. import decorators
from .. import jsonutils
from jsonpath_ng import parse
import aiostream.stream
    
async def templated_chunked(pipeline, items, input_key, prompt, summary_prompt, output_schema, **kw):
    async for item in pipelinemod.Pipeline({
            "steps": [
                {"chunk": {"input_key": input_key, **kw.get("chunking", {})}},
                {"each": {
                    "input_key": input_key,
                    "steps": [
                        {"templated": {
                            "prompt": prompt,
                            "output_schema": output_schema,
                            **kw.get("llm", {})}}]}},
                {"templated": {
                    "prompt": summary_prompt,
                    "output_schema": output_schema,
                    **kw.get("summary_llm", {})}}]}).run(items):
        yield item
