#! /usr/bin/env python
import unittest
import os
from config import basedir
from coverage import coverage
# from web.test.test_case import *


if __name__ == '__main__':  # pragma: no cover
    cov = coverage(branch=True, omit=['../.env/*', 'test/*'])
    cov.start()

    # from web.test.test_gravatar import *
    from test.test_gravatar import TestGravatar
    from test.test_case import TestCase

    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report()
    print("HTML version: " + os.path.join(basedir, ".coverage/index.html"))
    cov.html_report(directory='../.coverage')
    cov.erase()
