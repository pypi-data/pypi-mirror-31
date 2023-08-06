====================
sliding-rate-limiter
====================


.. image:: https://img.shields.io/pypi/v/sliding_rate_limiter.svg
        :target: https://pypi.python.org/pypi/sliding_rate_limiter

.. image:: https://img.shields.io/travis/kalibrr/sliding_rate_limiter.svg
        :target: https://travis-ci.org/kalibrr/sliding_rate_limiter

.. image:: https://readthedocs.org/projects/sliding-rate-limiter/badge/?version=latest
        :target: https://sliding-rate-limiter.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/kalibrr/sliding_rate_limiter/shield.svg
     :target: https://pyup.io/repos/github/kalibrr/sliding_rate_limiter/
     :alt: Updates


Sliding rate limiter using memory or a distributed Redis backend.


* Free software: Apache Software License 2.0
* Documentation: https://sliding-rate-limiter.readthedocs.io.


Features
--------

* Pluggable rate limiting backend (threadsafe in-memory or distributed Redis backend)

Usage
-----

.. code-block:: python

    from sliding_rate_limiter.region import RateLimiterRegion
    from sliding_rate_limiter.backends.memory import MemoryBackend

    region = RateLimiterRegion('default')
    region.configure(MemoryBackend())

    @region.rate_limit_on_arguments()
    def foo(user_id):
        pass

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

API heavily inspired by `dogpile.cache`_

.. _dogpile.cache: https://dogpilecache.readthedocs.io/en/latest/_
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
