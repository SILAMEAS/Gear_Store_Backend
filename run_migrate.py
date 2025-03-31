import os
from django.core.management import call_command
from django.http import JsonResponse

def migrate(request):
    call_command("migrate")
    return JsonResponse({"message": "Migrations applied successfully!"})
