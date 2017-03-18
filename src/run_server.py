#! /usr/bin/env python
from web import app


# import os
# import logging
# # logconfig = {"format": "%(asctime)s: [%(levelname)s]:\t%(message)s"}
debug = True
# debug = os.environ.get('DEBUG', False)
# if debug:
#    logging.getLogger().setLevel(logging.DEBUG)
#    # logconfig["level"] = logging.DEBUG
#    # logconfig["filename"] = "debug.log"
# # logging.basicConfig(**logconfig)


if __name__ == "__main__":
    app.run(debug=debug)