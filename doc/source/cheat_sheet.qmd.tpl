---
title: Ansys Actions
format: cheat_sheet-pdf
version: {{ version }}
footer: Getting started with Ansys action
footerlinks:
  - urls: 'https://actions.docs.ansys.com/version/stable/'
    text: Ansys action documentation
  - urls: 'https://github.com/ansys/actions/'
    text: Ansys action gitHub
execute:
    # output: false
    eval: false

latex-clean: true
jupyter:
  jupytext:
    text_representation:
      extension: .qmd
      format_name: quarto
      format_version: '1.0'
      jupytext_version: 1.16.1
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---
{% for example in examples %}
# {{ example.title }}
{{ example.description }}
```{python}
{{ example.code }}
```
{% endfor %}
