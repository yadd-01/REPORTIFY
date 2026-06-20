from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.shortcuts import resolve_url

class NoLoginAccountAdapter(DefaultAccountAdapter):
    def login(self, request, user):
        # Override to prevent auto-login ONLY after signup
        if 'signup' in request.path:
            return
        super().login(request, user)

    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        # Do not add 'logged_in' message during signup since we prevented auto-login
        if 'signup' in request.path and message_template == 'account/messages/logged_in.txt':
            return
        super().add_message(request, level, message_template, message_context, extra_tags)

    def get_signup_redirect_url(self, request):
        return resolve_url('account_login')
