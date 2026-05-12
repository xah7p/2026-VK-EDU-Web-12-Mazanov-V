from django.http import HttpRequest
from django.utils.http import url_has_allowed_host_and_scheme


def safe_redirect_url(request, url):
    if not url or not isinstance(url, str):
        return None
    url = url.strip()
    if not url:
        return None
    if url_has_allowed_host_and_scheme(
        url=url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return url
    return None
