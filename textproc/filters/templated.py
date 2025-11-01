import asyncio
import json
from jinja2 import Template
from jsonschema import validate, ValidationError
from jsonpath_ng import parse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import warnings

from .. import decorators

def jinja2jsonpath(template, data):
    context = {}
    expr_map = {}
    counter = 1

    for var in template.split("{{"):
        if "}}" in var:
            expr = var.split("}}")[0].strip()
            if expr.startswith("$") and expr not in expr_map:
                var_name = f"v{counter}"
                counter += 1
                if expr == "$":
                    context[var_name] = data
                    expr_map[expr] = var_name
                else:
                    jsonpath_expr = parse(expr)
                    matches = [match.value for match in jsonpath_expr.find(data)]
                    context[var_name] = matches if len(matches) > 1 else matches[0]
                    expr_map[expr] = var_name

    safe_template = template
    for expr, var_name in expr_map.items():
        safe_template = safe_template.replace(f"{{{{{expr}}}}}", f"{{{{{var_name}}}}}")

    return Template(safe_template).render(**context)

@decorators.map
async def templated(pipeline, item, prompt, output_schema, model_name="gpt-4", temperature=0.7, retry_limit=3):
    rendered_prompt = (jinja2jsonpath(prompt, item)
                       + f"\n\nRespond ONLY in valid JSON that matches this schema:\n{json.dumps(output_schema, indent=2)}")

    llm = ChatOpenAI(model_name=model_name, temperature=temperature)

    for idx in range(retry_limit):
        response = str(
            (await llm.ainvoke(rendered_prompt)).content
        ).strip().strip("```json").strip("```")
        
        try:
            llm_result_json = json.loads(response)
        except Exception as e:
            warnings.warn(f"LLM returned invalid JSON: {e}\n{response}", UserWarning)
            continue

        try:
            validate(instance=llm_result_json, schema=output_schema)
        except Exception as e:
            warnings.warn(f"LLM output does not conform to schema: {e}\n{llm_result_json}", UserWarning)
            continue

        if isinstance(item, dict) and isinstance(llm_result_json, dict):
            llm_result_json = {**item, **llm_result_json}
            
        return llm_result_json

    warnings.warn(f"FINAL LLM FAILURE IN templated", UserWarning)
    return {"failures": item.get("failures", []) + ["templated.schema_validation"], **item}
