"""Error emails that carry no member content.

Django's own error email includes the request, the URL, local variables and the
exception message, any of which can hold a members-only experience. This one is
built from a whitelist: the exception type, the view name and the code lines.
"""

import logging
import sys
import traceback

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

QUIET_SECONDS = 10 * 60


def view_name(request):
    match = getattr(request, "resolver_match", None)
    return match.view_name if match else "unknown view"


def code_lines(exc_info):
    frames = traceback.extract_tb(exc_info[2])
    return "\n".join(f"{f.filename}:{f.lineno} in {f.name}\n    {f.line}" for f in frames)


def notify(subject, body):
    """Email the steward. Never raises: the alert must not break the request it reports on."""
    if not settings.ALERT_EMAIL:
        return
    try:
        send_mail(subject, body, None, [settings.ALERT_EMAIL])
    except Exception as error:
        print(f"Could not email the steward: {type(error).__name__}", file=sys.stderr)


class AlertHandler(logging.Handler):
    # Not Handler.handleError anywhere here: it would print the log message, which holds the URL.
    def emit(self, record):
        if not (settings.ALERT_EMAIL and record.exc_info):
            return
        kind = record.exc_info[0].__name__
        where = view_name(getattr(record, "request", None))
        # One email per kind of error and place, so an outage doesn't flood the mailbox.
        if cache.add(f"alert:{kind}:{where}", True, QUIET_SECONDS):
            notify(f"Server error: {kind} in {where}", code_lines(record.exc_info))
