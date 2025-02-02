import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from .models import Factura,PagoStripe
from django.http import HttpResponse

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    return render(request, "home.html")
def checkout(request):
    return render(request, "checkout.html")


def create_checkout_session(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)

    if request.method == "POST":
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"Factura {factura.numero}",
                            },
                            "unit_amount": int(factura.total * 100),  # Stripe usa centavos
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=f"http://127.0.0.1:8000/facturacion/success/{factura.id}/",
                cancel_url=f"http://127.0.0.1:8000/facturacion/cancel/",
            )
            return JsonResponse({"id": session.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def payment_success(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    PagoStripe.objects.create(
        factura=factura,
        stripe_payment_id="PAGO_DE_PRUEBA",
        monto_pagado=factura.total
    )
    return render(request, "facturacion/success.html", {"factura": factura})

def payment_cancel(request):
    return render(request, "facturacion/cancel.html")

# Create your views here.
def index(request):
    return render(request, 'index.html')