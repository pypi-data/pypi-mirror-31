=====
Usage
=====

To use sliding-rate-limiter in a project::

    from sliding_rate_limiter.region import RateLimiterRegion
    from sliding_rate_limiter.backends.memory import MemoryBackend

    region = RateLimiterRegion('default')
    region.configure(MemoryBackend())

    @region.rate_limit_on_arguments()
    def foo(user_id):
        pass
