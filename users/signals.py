from django.utils import timezone
from graphql_jwt.signals import token_issued
from django.dispatch import receiver

@receiver(token_issued)
def update_last_login_on_token_issue(sender, request, user, **kwargs):
    """
    Update last_login when a JWT token is issued.
    """
    if user:
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])