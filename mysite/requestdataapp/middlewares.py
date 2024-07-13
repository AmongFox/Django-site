from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from .views import frequent_request_exception


def set_useragent_on_request(get_response):
    def middleware(request: HttpRequest):
        request.user_agent = request.META.get("HTTP_USER_AGENT")
        response = get_response(request)
        return response

    return middleware


class CountRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_count = 0
        self.response_count = 0
        self.exception_count = 0

    def __call__(self, request: HttpRequest):
        self.request_count += 1
        response = self.get_response(request)
        self.response_count += 1
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exception_count += 1
        print(f"Exception №{self.exception_count}")


class ThrottleMiddleware:
    def __init__(self, get_response, max_requests_per_minute=5):
        self.get_response = get_response
        self.max_requests_per_minute = max_requests_per_minute

    def __call__(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        cache_key = f'throttle_{ip_address}'
        print(f"Cache key: {cache.get(cache_key)}")

        if cache.get(cache_key) is None:
            cache.set(cache_key, 1, timeout=60)

        elif cache.get(cache_key) > self.max_requests_per_minute:
            return frequent_request_exception(request)
            # raise PermissionDenied("Too many requests from this IP address")

        else:
            cache.set(cache_key, cache.get(cache_key) + 1, timeout=60)

        response = self.get_response(request)
        return response
