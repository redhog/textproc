from .. import pipeline as pipelinemod
from .. import decorators
from .. import jsonutils
from jsonpath_ng import parse
import aiostream.stream
    
@decorators.map
async def each(pipeline, item, input_key, output_key = None, **kw):
    if output_key is None: output_key = input_key
    jsonutils.set_by_path(
        item,
        output_key,
        await aiostream.stream.list(
            pipelinemod.Pipeline(kw).run(
                jsonutils.flatten_matches(parse(input_key).find(item)))))
    return item
            
