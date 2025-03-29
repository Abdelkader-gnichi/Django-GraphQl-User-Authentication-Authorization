# users/mutations.py
import graphene
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import (
    UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str # Use force_str instead of force_text
from graphql_jwt.decorators import login_required

from .schema import UserType # Import the UserType we defined

UserModel = get_user_model()

# --- Helper function for form errors ---
def get_form_errors(form):
    """Extracts form errors into a list of strings."""
    errors = []
    for field, field_errors in form.errors.items():
        for error in field_errors:
            errors.append(f"{field.replace('_', ' ').title()}: {error}")
    return errors

# --- Registration ---
class RegisterMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        password2 = graphene.String(required=True)

    success = graphene.Boolean()
    user = graphene.Field(UserType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, username, email, password, password2):
        if password != password2:
            return RegisterMutation(success=False, errors=["Passwords do not match."])

        form = UserCreationForm({'username': username, 'email': email, 'password': password}) # Password2 handled by form

        if form.is_valid():
            user = form.save()
            # Optional: Add logic here like sending a verification email
            return RegisterMutation(success=True, user=user)
        else:
            return RegisterMutation(success=False, errors=get_form_errors(form))


# --- Password Reset Request ---
class RequestPasswordResetMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, email):
        form = PasswordResetForm({'email': email})
        if form.is_valid():
            # You NEED to configure email settings in settings.py for this to work!
            # You might want to pass domain/site info for the email link
            # from_email could be customized
            # email_template_name etc can be overridden
            form.save(
                request=info.context, # Pass request for domain/site info if needed by templates
                use_https=info.context.is_secure(),
                # subject_template_name='registration/password_reset_subject.txt', # Optional
                # email_template_name='registration/password_reset_email.html',   # Optional
                # # domain_override=frontend_domain,
                # extra_email_context= {
                #     'reset_url': frontend_path,  # This will be available in the email template
                # }
            )
            return RequestPasswordResetMutation(success=True)
        else:
            # Avoid revealing if the email exists - return success even if invalid
            # Or provide a generic error message
            # return RequestPasswordResetMutation(success=False, errors=get_form_errors(form))
            return RequestPasswordResetMutation(success=True) # More secure approach


# --- Set New Password (after reset request) ---
class PasswordSetMutation(graphene.Mutation):
    class Arguments:
        uidb64 = graphene.String(required=True)
        token = graphene.String(required=True)
        new_password1 = graphene.String(required=True)
        new_password2 = graphene.String(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, uidb64, token, new_password1, new_password2):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = SetPasswordForm(user, {'new_password1': new_password1, 'new_password2': new_password2})
            if form.is_valid():
                form.save()
                return PasswordSetMutation(success=True)
            else:
                return PasswordSetMutation(success=False, errors=get_form_errors(form))
        else:
            # Invalid token or user
            return PasswordSetMutation(success=False, errors=["Invalid password reset link."])


# --- Change Password (for logged-in user) ---
class PasswordChangeMutation(graphene.Mutation):
    class Arguments:
        old_password = graphene.String(required=True)
        new_password1 = graphene.String(required=True)
        new_password2 = graphene.String(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required # Protect this mutation
    @staticmethod
    def mutate(root, info, old_password, new_password1, new_password2):
        user = info.context.user
        form = PasswordChangeForm(user, {
            'old_password': old_password,
            'new_password1': new_password1,
            'new_password2': new_password2,
        })

        if form.is_valid():
            form.save()
            # Optional: Update session auth hash if using sessions alongside JWT
            # from django.contrib.auth import update_session_auth_hash
            # update_session_auth_hash(info.context, form.user)
            return PasswordChangeMutation(success=True)
        else:
            return PasswordChangeMutation(success=False, errors=get_form_errors(form))


# --- Combine all mutations ---
class AuthMutation(graphene.ObjectType):
    register = RegisterMutation.Field()
    request_password_reset = RequestPasswordResetMutation.Field()
    password_set = PasswordSetMutation.Field() # Name avoids conflict if using relay
    password_change = PasswordChangeMutation.Field()