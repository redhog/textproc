import asyncio
import json
from jinja2 import Template
from jsonschema import validate, ValidationError
from jsonpath_ng import parse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import warnings
import re
import logging

from .. import decorators

logger = logging.getLogger(__name__)

def jinja2jsonpath(template, data):
    context = {}
    expr_map = {}
    counter = 1

    # Regex to find {{ ... }} and {% ... %}
    token_pattern = re.compile(r"({{.*?}}|{%.*?%})")

    def replace_expr(match):
        nonlocal counter
        token = match.group(0)
        expr_pattern = re.compile(r"(\$\.[\w\[\]\.]+|\$)")

        def repl(expr_match):
            nonlocal counter
            expr = expr_match.group(0)
            if expr not in expr_map:
                var_name = f"v{counter}"
                counter += 1
                if expr == "$":
                    context[var_name] = data
                else:
                    jsonpath_expr = parse(expr)
                    matches = [m.value for m in jsonpath_expr.find(data)]
                    if not matches: raise KeyError("%s in %s" % (expr, str(data)[:400]))
                    context[var_name] = matches if len(matches) > 1 else matches[0]
                expr_map[expr] = var_name
            return expr_map[expr]

        new_token = expr_pattern.sub(lambda m: repl(m), token)
        return new_token

    safe_template = token_pattern.sub(replace_expr, template)

    return Template(safe_template).render(**context)

@decorators.map
async def templated(pipeline, item, prompt, output_schema, model_name="gpt-5-mini-2025-08-07", temperature=0.7, retry_limit=3):
    rendered_prompt = (jinja2jsonpath(prompt, item)
                       + f"\n\nRespond ONLY in valid JSON that matches this schema:\n{json.dumps(output_schema, indent=2)}")

    llm = ChatOpenAI(model_name=model_name, temperature=temperature)

    for idx in range(retry_limit):
        response = ""
        try:
            logger.info("LLM call")
            response = await llm.ainvoke(rendered_prompt)
            response = str(
                (response).content
            ).strip().strip("```json").strip("```")
            
            llm_result_json = json.loads(response)
            validate(instance=llm_result_json, schema=output_schema)
        except Exception as e:
            warnings.warn(f"LLM call failed: {e}\n{response}", UserWarning)
            await asyncio.sleep(2) # Don't trip rate limit
            continue

        if isinstance(item, dict) and isinstance(llm_result_json, dict):
            llm_result_json = {**item, **llm_result_json}
            
        return llm_result_json

    warnings.warn(f"FINAL LLM FAILURE IN templated", UserWarning)
    return {"failures": item.get("failures", []) + ["templated.schema_validation"], **item}
