# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


import pytest

from sliding_rate_limiter.utils import parse_limit, function_key_generator


def test_function_key_generator():
    import logging.config
    key_generator = function_key_generator(logging.config.dictConfig)
    assert key_generator(1, 'foo') == 'logging.config:dictConfig|r|1 foo'
    assert key_generator() == 'logging.config:dictConfig|r|'
    assert key_generator('fooz') == 'logging.config:dictConfig|r|fooz'

    key_generator = function_key_generator(logging.config.dictConfig, 'space')
    assert key_generator(1, 'foo') == 'logging.config:dictConfig|space|r|1 foo'
    assert key_generator() == 'logging.config:dictConfig|space|r|'
    assert key_generator('fooz') == 'logging.config:dictConfig|space|r|fooz'


def test_parse_limit():
    limit, window = parse_limit('5/s')
    assert limit == 5
    assert window == 1

    limit, window = parse_limit('5/10s')
    assert limit == 5
    assert window == 10

    limit, window = parse_limit('9/2h')
    assert limit == 9
    assert window == 7200

    with pytest.raises(ValueError):
        parse_limit('9/0.5h')
        parse_limit('9/5w')
