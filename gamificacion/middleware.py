# gamificacion/middleware.py
from django.utils import timezone
from django.db import transaction
import logging

from .models import PuntosUsuario
from .signals import PUNTOS_POR_LOGIN_DIARIO
logger = logging.getLogger(__name__)

class DailyRewardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("--- INICIO DailyRewardMiddleware ---")
        print(f"Request path: {request.path}") # Para ver qué ruta activa el middleware

        if request.user.is_authenticated:
            print(f"Usuario autenticado: {request.user.username} (ID: {request.user.id})")
            today = timezone.localdate(timezone.now())
            print(f"DEBUG: today (localdate): {today}")

            try:
                puntos_usuario = PuntosUsuario.objects.get(usuario=request.user) # No uses select_for_update en este debug, para simplificar.
                db_last_reward_date = puntos_usuario.last_daily_reward_date
                print(f"DEBUG: last_daily_reward_date de DB: {db_last_reward_date}")

                condition_result = False
                if not db_last_reward_date:
                    condition_result = True
                    print("DEBUG: db_last_reward_date es None/vacío. Condición CUMPLIDA.")
                elif db_last_reward_date < today:
                    condition_result = True
                    print(f"DEBUG: {db_last_reward_date} < {today}. Condición CUMPLIDA.")
                else:
                    print(f"DEBUG: {db_last_reward_date} NO es menor que {today}. Condición NO CUMPLIDA.")

                if condition_result:
                    print("DEBUG: PROCEDIENDO a otorgar puntos y guardar...")
                    # Aquí, *dentro de un bloque transaction.atomic() real* harías el save
                    # Pero para esta depuración, lo vemos fuera primero si es necesario.
                    # Para no alterar la DB en cada intento, SOLO PONDREMOS EL PRINT AQUI
                    puntos_usuario.puntos += PUNTOS_POR_LOGIN_DIARIO
                    puntos_usuario.last_daily_reward_date = today
                    # puntos_usuario.save(update_fields=['puntos', 'last_daily_reward_date']) # COMENTA ESTA LINEA TEMPORALMENTE
                    print(f"DEBUG: Se deberían haber sumado {PUNTOS_POR_LOGIN_DIARIO} puntos. Nuevo total simulado: {puntos_usuario.puntos}")
                    logger.debug(f"{request.user.username} ha recibido {PUNTOS_POR_LOGIN_DIARIO} puntos por login diario. Total (simulado): {puntos_usuario.puntos}")

                else:
                    print("DEBUG: No se otorgan puntos. Ya se otorgaron hoy o fecha futura.")

            except PuntosUsuario.DoesNotExist:
                print(f"ADVERTENCIA: PuntosUsuario no encontrado para {request.user.username}.")
            except Exception as e:
                print(f"ERROR: Fallo inesperado en middleware para {request.user.username}: {e}")
        else:
            print("Usuario NO autenticado. No se procesa el middleware de puntos diarios.")

        print("--- FIN DailyRewardMiddleware ---")
        return self.get_response(request)