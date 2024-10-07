from django.shortcuts import redirect
from django.urls import resolve

class EmployeeLoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_url = resolve(request.path_info).url_name
        # Allow unauthenticated access only to the login page
        if not request.session.get('employee_id') and current_url not in ['login']:
            return redirect('login')
        return self.get_response(request)
