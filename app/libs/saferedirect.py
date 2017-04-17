from flask import request, redirect, url_for
from urlparse import urlparse, urljoin

__all__ = ['redirect_back']

def is_safe_url(target):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))
	return test_url.scheme in ('http', 'https') and \
		ref_url.netloc == test_url.netloc

def redirect_back(endpoint, **values):
	target = request.form.get('next')
	if not target or not is_safe_url(target):
		target = url_for(endpoint, **values)
	return redirect(target)