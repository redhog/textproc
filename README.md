# Textproc

This repository contains a minimalistic text processing pipeline framework. Notable features:

* Fully asynchronous
* Supports parallel LLM/web scraping calls
* Uses langchain
* Can fetch wikipedia articles
* jinja2 templates for prompts
* jsonpaths for fetching data items

See the [full pipeline example](Full%20pipeline.ipynb) for further details.

# Possible future development

* Use keybert for keyword extraction
* Pairwize comparison for deduplication or entries (with semantic distance culling to not get O(n^2) complexity)

# Author & license

Copyright 2025 by Egil Moeller
Licensed under GPL 3.
