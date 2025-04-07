from django.utils.deprecation import MiddlewareMixin


class UserThemeMiddleware(MiddlewareMixin):
    """
    Middleware to include user's theme preference in the template context.

    This allows templates to access the user's theme without explicitly passing it
    from each view.
    """

    def process_template_response(self, request, response):
        if hasattr(response, 'context_data') and hasattr(request, 'user') and request.user.is_authenticated:
            try:
                response.context_data['user_theme'] = request.user.profile.theme
            except (AttributeError, Exception):
                # If profile or theme doesn't exist, do nothing
                pass
        return response
