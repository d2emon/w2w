import wikipedia
import re


WIKI_PROPERTIES = {
    'P18': 'image',
    'P57': 'director',
    'P58': 'screenplay',
    'P86': 'composer',
    'P136': 'genre',
    'P161': 'starring',
    'P162': 'producer',
    'P170': 'author',
    'P272': 'company',
    'P344': 'cinematography',
    'P345': 'IMDB',
    'P364': 'lang',
    'P407': 'lang',
    'P449': 'channel',
    'P495': 'country',
    'P577': 'release',
    'P580': 'on_screen_start',
    'P582': 'on_screen_end',
    'P856': 'site',
    'P1113': 'episodes',
    'P1431': 'executive_producer',
    'P1705': 'original_title',
    'P1811': 'episode_list',
    'P1851': 'episodesi1',
    'P2047': 'length',
    'P2130': 'budget',
    'P2142': 'box_office',
    'P2437': 'seasons',
}


def parse_wiki(page):
    wikipedia.set_lang('ru')
    print("Page=", page)
    try:
        p = wikipedia.page(page)
        parsed = {
            "query": page,
            "page": p,
        }
        title = p.title
        summary = p.summary
        t = p.html()
        res = re.findall(r'<span.*?\sdata\-wikidata\-property\-id="(.*?)".*?>(.*?)</span>', t)
        # r1 = re.findall(r'<td(.*?)>(.*?)</td>', t)
        # r2 = re.findall(r'<span(.*?)data\-wikidata\-property\-id\=\"(.*?)\">(.*?)</span(.*?)>', t)
        # print('='*80)
        # print(t)
        # print('='*80)
        # for r in r1:
        #    # print(r)
        # print('='*80)
        # for r in r2:
        #    # print(r)
        # print('='*80)
    except:
        parsed = {
            "query": page,
            "page": None,
        }
        title = page
        summary = ''
        res = []

    # print(res)
    props = dict()
    for k, v in res:
        # print(k, v)
        prop_key = WIKI_PROPERTIES.get(k, k)
        val = props.get(prop_key)
        # print("V", val)
        if val is None:
            props[prop_key] = v
        else:
            # print("VAL", val)
            if type(val) is list:
                val.append(v)
            else:
                props[prop_key] = [val, v]
    parsed['properties'] = props
    parsed['movie'] = {
        'title': title,
        'summary': summary,

        'original_title': props.get('original_title'),
        'image': parse_image(props.get('image')),

        'genre': parse_link(props.get('genre')),
        'author': parse_link(props.get('author')),
        'starring': parse_link(props.get('starring')),
        'composer': parse_link(props.get('composer')),
        'country': parse_tag(props.get('country')),
        'lang': parse_link(props.get('lang')),
        'seasons': props.get('seasons'),
        'episodes': props.get('episodes'),

        'executive_producer': parse_link(props.get('executive_producer')),
        'producer': parse_link(props.get('producer')),
        'director': parse_link(props.get('director')),
        'screenplay': parse_link(props.get('screenplay')),
        'cinematography': parse_link(props.get('cinematography')),
        'company': parse_link(props.get('company')),
        'length': props.get('length'),
        'budget': parse_tag(props.get('budget')),
        'box_office': parse_tag(props.get('box_office')),
        'release': parse_link(props.get('release')),

        'channel': parse_link(props.get('channel')),
        'on_screen': [
            props.get('on_screen_start'),
            props.get('on_screen_end'),
        ],

        'site': parse_url(props.get('site')),
        'IMDB': parse_link(props.get('IMDB')),
    }
    return parsed


def parse_image(image):
    if image is None:
        return None
    res = re.search(r'<img.*src="(.*?)".*>', image).group(1)
    return res


def parse_link(text):
    if text is None:
        return None
    if type(text) is list:
        text = "\n".join(text)
    res = re.findall(r'<a.*?>(.*?)</a>', text)
    if not res:
        res = [text, ]
    return parse_tag(res)


def parse_url(text):
    if text is None:
        return None
    if type(text) is list:
        text = "\n".join(text)
    res = re.findall(r'href="(.*?)"', text)
    if not res:
        return [text, ]
    return res


def parse_span(text):
    if text is None:
        return None
    if type(text) is list:
        text = "\n".join(text)
    res = re.findall(r'<span.*>(.*)', text)
    if not res:
        return [text, ]
    return res


def parse_tag(text):
    if text is None:
        return None
    if type(text) is not list:
        text = [text, ]
    res = []
    for t in text:
        t = re.sub(r'<.*?>', '', t)
        t = re.sub(r'\[.*?\]', '', t)
        if t:
            res.append(t)
    if not res:
        return [text, ]
    return res
