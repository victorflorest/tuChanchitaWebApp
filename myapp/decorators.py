from functools import wraps
from django.shortcuts import redirect

def session_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return redirect('login')  # Asegúrate que exista una URL llamada 'login'
        return view_func(request, *args, **kwargs)
    return _wrapped_view