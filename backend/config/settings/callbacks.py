from django.utils import timezone

# NÃO importe User aqui no topo!
# from django.contrib.auth.models import User  <- REMOVA ISSO


def environment_callback(request):
    """Badge de ambiente no topo do admin"""
    import os

    env = os.environ.get("DJANGO_SETTINGS_MODULE", "")

    if "production" in env:
        return ["Production", "danger"]
    elif "staging" in env:
        return ["Staging", "warning"]
    else:
        return ["Development", "info"]


def dashboard_callback(request, context):
    """Widgets personalizados no dashboard"""

    # Importe DENTRO da função, não no topo do arquivo
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Contadores
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()

    # Novos usuários hoje
    today = timezone.now().date()
    new_today = User.objects.filter(date_joined__date=today).count()

    context.update({
        "kpi": [
            {
                "title": "Total de Usuários",
                "metric": total_users,
                "footer": f"{active_users} ativos • {staff_users} staff",
                "chart": "👥",
            },
            {
                "title": "Novos Hoje",
                "metric": new_today,
                "footer": "Cadastrados nas últimas 24h",
                "chart": "📈",
            },
        ]
    })

    return context
