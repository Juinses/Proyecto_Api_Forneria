from django.shortcuts import render


def csrf_failure(request, reason=""):
    """Vista personalizada para fallos CSRF.

    Renderiza una plantilla clara y devuelve 403 para que el frontend
    pueda mostrar una alerta amigable en lugar del HTML crudo.
    """
    return render(request, 'csrf_failure.html', {'reason': reason}, status=403)