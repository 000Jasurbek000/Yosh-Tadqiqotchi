"""SMTP: IPv4 + timeout. cPanel'da Errno 99 (IPv6 bind) ni oldini oladi."""
import socket
import smtplib
import logging
import threading

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend

logger = logging.getLogger(__name__)


class IPv4EmailBackend(SMTPBackend):
    """Gmail/cPanel uchun faqat IPv4 orqali ulanish."""

    def open(self):
        if self.connection:
            return False

        original_getaddrinfo = socket.getaddrinfo
        original_has_ipv6 = getattr(socket, 'has_ipv6', True)
        timeout = self.timeout if self.timeout is not None else getattr(settings, 'EMAIL_TIMEOUT', 8)
        host = self.host
        if host in ('localhost', '::1', '[::1]'):
            host = '127.0.0.1'

        def ipv4_only(name, port, family=0, type=0, proto=0, flags=0):
            return original_getaddrinfo(name, port, socket.AF_INET, type or socket.SOCK_STREAM, proto, flags)

        try:
            socket.getaddrinfo = ipv4_only
            socket.has_ipv6 = False
            conn_kwargs = {
                'host': host,
                'port': self.port,
                'timeout': timeout,
                'local_hostname': 'localhost',
            }
                if self.use_ssl:
                    ctx = getattr(self, 'ssl_context', None)
                    if ctx:
                        conn_kwargs['context'] = ctx
                    self.connection = smtplib.SMTP_SSL(**conn_kwargs)
            else:
                self.connection = smtplib.SMTP(**conn_kwargs)
            self.connection.ehlo()
            if self.use_tls:
                ctx = getattr(self, 'ssl_context', None)
                if ctx:
                    self.connection.starttls(context=ctx)
                else:
                    self.connection.starttls()
                self.connection.ehlo()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False
        finally:
            socket.getaddrinfo = original_getaddrinfo
            socket.has_ipv6 = original_has_ipv6


def send_email_async(email_message):
    """So'rovni SMTP kutishiga qotirib qo'ymaslik (100 ta foydalanuvchi)."""

    def _run():
        try:
            email_message.send(fail_silently=True)
        except Exception:
            logger.exception('Email yuborilmadi')

    threading.Thread(target=_run, daemon=True, name='email-send').start()


def send_mail_async(subject, message, from_email, recipient_list, **kwargs):
    recipients = [r for r in (recipient_list or []) if r]
    if not recipients:
        return
    msg = EmailMessage(subject, message, from_email, recipients)
    send_email_async(msg)
