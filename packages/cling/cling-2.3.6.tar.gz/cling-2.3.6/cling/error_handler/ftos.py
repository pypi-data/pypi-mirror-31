# -*- coding: utf-8 -*-

"""
Error handler tailored for Force 10 devices.
"""

import re

from .default import DefaultErrorHandler


class FtosErrorHandler(DefaultErrorHandler):
    _ERROR_MATCHES = [
        re.compile(r'^%.+invalid', flags=re.I | re.M),
        re.compile(r'^%.+unknown', flags=re.I | re.M),
        re.compile(r'^%.+ambiguous', flags=re.I | re.M),
        re.compile(r'^%.+incomplete', flags=re.I | re.M),
        re.compile(r'^%.+failed', flags=re.I | re.M),
    ]

    def __init__(self, personality):
        super(FtosErrorHandler, self).__init__(personality)

    def has_error(self, output):
        # Code that detects _ERROR_MSGS in output
        # if any(err in output for err in self._ERROR_MSGS):
        #    return True
        # Match _ERROR_MATCHES in output
        if any(m.search(output) for m in self._ERROR_MATCHES):
            return True
        return False
