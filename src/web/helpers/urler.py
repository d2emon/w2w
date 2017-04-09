from jinja2 import Markup
from flask import request, url_for


class urler:
    def __init__(self, endpoint='', slugs=dict()):
        if not endpoint:
            endpoint = request.endpoint
        self.endpoint = endpoint
        self.slugs = dict((k, v) for k, v in slugs.items() if v)

    def render(self, **get_vars):
        if self.endpoint is None:
            return ""
        self.slugs.update(get_vars)
        return url_for(self.endpoint, **self.slugs)
        # Markup("<script>\ndocument.write(moment(\"{}\").{});\n</script>".format(self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))
