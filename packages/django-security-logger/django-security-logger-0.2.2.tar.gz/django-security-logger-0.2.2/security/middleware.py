import traceback

from ipware.ip import get_ip

from django import http
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.transaction import get_connection
from django.urls import is_valid_path
from django.utils.encoding import force_text

try:
    from django.core.urlresolvers import get_callable
except ImportError:
    from django.urls import get_callable

from .config import (
    SECURITY_DEFAULT_THROTTLING_VALIDATORS_PATH, SECURITY_LOG_IGNORE_IP, SECURITY_THROTTLING_FAILURE_VIEW
)
from .exception import ThrottlingException
from .models import InputLoggedRequest


try:
    from importlib import import_module
except ImportError:  # For Django < 1.8
    from django.utils.importlib import import_module


try:
    THROTTLING_VALIDATORS = getattr(import_module(SECURITY_DEFAULT_THROTTLING_VALIDATORS_PATH), 'default_validators')
except ImportError:
    raise ImproperlyConfigured('Configuration DEFAULT_THROTTLING_VALIDATORS does not contain valid module')


class MiddlewareMixin:

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        response = response or self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


class LogMiddleware(MiddlewareMixin):

    response_redirect_class = http.HttpResponsePermanentRedirect

    def process_request(self, request):
        if get_ip(request) not in SECURITY_LOG_IGNORE_IP:
            request._logged_request = InputLoggedRequest.objects.prepare_from_request(request)

        connection = get_connection()
        logged_requests_list = getattr(connection, 'logged_requests', [])
        logged_requests_list.append([])
        connection.logged_requests = logged_requests_list

        # Return a redirect if necessary
        if self.should_redirect_with_slash(request):
            return self.response_redirect_class(self.get_full_path_with_slash(request))

    def get_full_path_with_slash(self, request):
        """
        Return the full path of the request with a trailing slash appended.

        Raise a RuntimeError if settings.DEBUG is True and request.method is
        POST, PUT, or PATCH.
        """
        new_path = request.get_full_path(force_append_slash=True)
        if settings.DEBUG and request.method in {'POST', 'PUT', 'PATCH'}:
            raise RuntimeError(
                "You called this URL via %(method)s, but the URL doesn't end "
                "in a slash and you have SECURITY_APPEND_SLASH set. Django can't "
                "redirect to the slash URL while maintaining %(method)s data. "
                "Change your form to point to %(url)s (note the trailing "
                "slash), or set SECURITY_APPEND_SLASH=False in your Django settings." % {
                    'method': request.method,
                    'url': request.get_host() + new_path,
                }
            )
        return new_path

    def should_redirect_with_slash(self, request):
        """
        Return True if settings.APPEND_SLASH is True and appending a slash to
        the request path turns an invalid path into a valid one.
        """
        if getattr(settings, 'SECURITY_APPEND_SLASH', True) and not request.get_full_path().endswith('/'):
            urlconf = getattr(request, 'urlconf', None)
            return (
                not is_valid_path(request.path_info, urlconf) and
                is_valid_path('{}/'.format(request.path_info), urlconf)
            )
        return False

    def _render_throttling(self, request, exception):
        return get_callable(SECURITY_THROTTLING_FAILURE_VIEW)(request, exception)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if getattr(request, '_logged_request', False):

            # Exempt all logs
            if getattr(callback, 'log_exempt', False):
                del request._logged_request

            # TODO: this is not the best solution if the request throw exception inside process_request of some Middleware
            # the bode will be included (But I didn't have better solution now)
            if getattr(callback, 'hide_request_body', False):
                request._logged_request.request_body = ''

            # Check if throttling is not exempted
            if not getattr(callback, 'throttling_exempt', False):
                try:
                    for validator in THROTTLING_VALIDATORS:
                        validator.validate(request)
                except ThrottlingException as exception:
                    return self.process_exception(request, exception)

    def process_response(self, request, response):
        input_logged_request = getattr(request, '_logged_request', None)
        if input_logged_request:
            input_logged_request.update_from_response(response)
            input_logged_request.save()

        connection = get_connection()
        logged_requests = connection.logged_requests.pop() if hasattr(connection, 'logged_requests') else ()
        [logged_request.create(input_logged_request) for logged_request in logged_requests]
        return response

    def process_exception(self, request, exception):
        if hasattr(request, '_logged_request'):
            logged_request = request._logged_request
            logged_request.error_description = traceback.format_exc()
            logged_request.exception_name = exception.__class__.__name__
            if isinstance(exception, ThrottlingException):
                logged_request.type = InputLoggedRequest.THROTTLED_REQUEST
                return self._render_throttling(request, exception)
