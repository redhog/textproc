from langchain_text_splitters import MarkdownTextSplitter
from jsonpath_ng import parse

from .. import decorators
from .. import jsonutils

@decorators.map
async def chunk(pipeline, item, input_key, output_key = None, **kw):
    if output_key is None: output_key = input_key

    jsonutils.set_by_path(
        item,
        output_key,
        MarkdownTextSplitter(
            **kw
        ).split_text(parse(input_key).find(item)[0].value))
    
    return item
