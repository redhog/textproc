from jsonpath_ng import parse

def set_by_path(item, key, value):
    if "." in key:
        path, name = key.rsplit(".", 1)
    parse(path).find(item)[0].value[name] = value

def flatten_matches(matches):
    for match in matches:
        if isinstance(match.value, list):
            for value in match.value:
                yield value
        else:
            yield match.value
