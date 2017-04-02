import wikipedia
import re


def parse_wiki(page):
    wikipedia.set_lang('ru')
    p = wikipedia.page(page)
    parsed = {
        "query": page,
        "page": p,
    }
    t = p.html()
    res = re.findall(r'<span.*\sdata-wikidata-property-id="(.*?)".*?>(.*)</span>', t)
    props = []
    for f in res:
        props.append(f)
    parsed['properties'] = dict(props)
    return parsed
