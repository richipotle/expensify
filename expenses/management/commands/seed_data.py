"""
Comando de gestión que crea datos de demostración (seed data).

Crea usuarios, cuentas bancarias, gastos y pagos de ejemplo cubriendo los
distintos estados del sistema, usando siempre las funciones de
``services.py`` de cada app para respetar las reglas de negocio (nunca se
crean objetos "a mano" que violen invariantes).

El comando es idempotente: los datos de demostración se identifican con el
prefijo ``demo_`` en los nombres de usuario. Si ya existen, el comando no
duplica nada y simplemente informa que los datos ya fueron creados.

Uso:
    python manage.py seed_data
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import BankAccount
from expenses.models import Expense
from expenses.services import aprobar_gasto, cancelar_gasto
from payments.services import aprobar_pago, cancelar_pago, crear_pago, efectuar_pago

# Prefijo usado para marcar (e identificar) los usuarios de demostración.
DEMO_USER_PREFIX = "demo_"


class Command(BaseCommand):
    help = (
        "Crea usuarios, cuentas bancarias, gastos y pagos de demostración "
        "cubriendo los distintos estados del sistema. Es idempotente: si "
        "los datos de demostración ya existen (usuarios con prefijo "
        "'demo_'), no duplica nada."
    )

    def handle(self, *args, **options):
        User = get_user_model()

        if User.objects.filter(username=f"{DEMO_USER_PREFIX}gerente").exists():
            self.stdout.write(
                self.style.WARNING(
                    "Los datos de demostración ya existen (se detectó el "
                    f"usuario '{DEMO_USER_PREFIX}gerente'). No se creó "
                    "nada nuevo."
                )
            )
            return

        with transaction.atomic():
            usuarios = self._crear_usuarios(User)
            cuentas = self._crear_cuentas_bancarias()
            gastos = self._crear_gastos(usuarios)
            pagos = self._crear_pagos(usuarios, cuentas, gastos)

        self.stdout.write(
            self.style.SUCCESS(
                f"Datos de demostración creados: {len(usuarios)} usuarios, "
                f"{len(cuentas)} cuentas bancarias, {len(gastos)} gastos y "
                f"{len(pagos)} pagos."
            )
        )

    def _crear_usuarios(self, User):
        datos_usuarios = [
            {
                "username": f"{DEMO_USER_PREFIX}gerente",
                "email": "demo_gerente@example.com",
                "first_name": "Gerente",
                "last_name": "Demo",
                "is_staff": True,
            },
            {
                "username": f"{DEMO_USER_PREFIX}contador",
                "email": "demo_contador@example.com",
                "first_name": "Contador",
                "last_name": "Demo",
                "is_staff": False,
            },
            {
                "username": f"{DEMO_USER_PREFIX}asistente",
                "email": "demo_asistente@example.com",
                "first_name": "Asistente",
                "last_name": "Demo",
                "is_staff": False,
            },
        ]

        usuarios = {}
        for datos in datos_usuarios:
            usuario = User(
                username=datos["username"],
                email=datos["email"],
                first_name=datos["first_name"],
                last_name=datos["last_name"],
                is_staff=datos["is_staff"],
            )
            usuario.set_password("Demo12345!")
            usuario.save()
            usuarios[datos["username"]] = usuario
            self.stdout.write(f"Usuario creado: {usuario.username}")

        return usuarios

    def _crear_cuentas_bancarias(self):
        datos_cuentas = [
            {
                "nombre": "Cuenta Demo Principal",
                "banco": "Banco Nacional",
                "numero_cuenta": "1001",
                "saldo_actual": Decimal("50000.00"),
                "moneda": BankAccount.Moneda.USD,
            },
            {
                "nombre": "Cuenta Demo Operativa",
                "banco": "Banco Regional",
                "numero_cuenta": "1002",
                "saldo_actual": Decimal("20000.00"),
                "moneda": BankAccount.Moneda.MXN,
            },
            {
                "nombre": "Cuenta Demo Marketing",
                "banco": "Banco Internacional",
                "numero_cuenta": "1003",
                "saldo_actual": Decimal("15000.00"),
                "moneda": BankAccount.Moneda.EUR,
            },
        ]

        cuentas = []
        for datos in datos_cuentas:
            cuenta = BankAccount.objects.create(**datos)
            cuentas.append(cuenta)
            self.stdout.write(f"Cuenta bancaria creada: {cuenta.nombre}")

        return cuentas

    def _crear_gastos(self, usuarios):
        gerente = usuarios[f"{DEMO_USER_PREFIX}gerente"]

        # 1. BORRADOR
        gasto_viaje_monterrey = Expense.objects.create(
            titulo="Demo - Viaje de ventas a Monterrey",
            descripcion="Viáticos para reunión con clientes en Monterrey.",
            monto_total=Decimal("3200.00"),
            categoria=Expense.Categoria.VIATICOS,
            fecha=date(2024, 1, 15),
            creado_por=gerente,
        )

        # 2. BORRADOR
        gasto_papeleria = Expense.objects.create(
            titulo="Demo - Papelería y suministros de oficina",
            descripcion="Compra trimestral de papelería y suministros.",
            monto_total=Decimal("850.00"),
            categoria=Expense.Categoria.SUMINISTROS,
            fecha=date(2024, 1, 20),
            creado_por=gerente,
        )

        # 3. APROBADO (con un pago PENDIENTE asociado)
        gasto_internet = Expense.objects.create(
            titulo="Demo - Servicio de internet corporativo",
            descripcion="Pago mensual de internet para la oficina.",
            monto_total=Decimal("1500.00"),
            categoria=Expense.Categoria.SERVICIOS,
            fecha=date(2024, 2, 1),
            creado_por=gerente,
        )
        aprobar_gasto(gasto_internet, gerente)

        # 4. APROBADO (con un pago APROBADO asociado, sin efectuar)
        gasto_marketing = Expense.objects.create(
            titulo="Demo - Campaña de marketing digital",
            descripcion="Campaña publicitaria en redes sociales.",
            monto_total=Decimal("6000.00"),
            categoria=Expense.Categoria.MARKETING,
            fecha=date(2024, 2, 5),
            creado_por=gerente,
        )
        aprobar_gasto(gasto_marketing, gerente)

        # 5. PAGADO (un pago EFECTUADO que cubre el monto total)
        gasto_nomina = Expense.objects.create(
            titulo="Demo - Nómina quincenal",
            descripcion="Pago de nómina de la primera quincena.",
            monto_total=Decimal("10000.00"),
            categoria=Expense.Categoria.NOMINA,
            fecha=date(2024, 2, 10),
            creado_por=gerente,
        )
        aprobar_gasto(gasto_nomina, gerente)

        # 6. PAGADO (dos pagos EFECTUADOS que cubren el monto total)
        gasto_renta = Expense.objects.create(
            titulo="Demo - Renta de oficina",
            descripcion="Renta mensual de las oficinas centrales.",
            monto_total=Decimal("8000.00"),
            categoria=Expense.Categoria.SERVICIOS,
            fecha=date(2024, 2, 15),
            creado_por=gerente,
        )
        aprobar_gasto(gasto_renta, gerente)

        # 7. CANCELADO (cancelado directamente desde BORRADOR, sin pagos)
        gasto_equipo = Expense.objects.create(
            titulo="Demo - Compra de equipo de cómputo",
            descripcion="Compra de laptops que finalmente no se realizó.",
            monto_total=Decimal("4500.00"),
            categoria=Expense.Categoria.OTROS,
            fecha=date(2024, 1, 25),
            creado_por=gerente,
        )
        cancelar_gasto(gasto_equipo, gerente)

        # 8. CANCELADO (aprobado, con un pago cancelado, y luego cancelado)
        gasto_viaje_guadalajara = Expense.objects.create(
            titulo="Demo - Viaje cancelado a Guadalajara",
            descripcion="Viaje de negocios que se cancela por cambio de planes.",
            monto_total=Decimal("2200.00"),
            categoria=Expense.Categoria.VIATICOS,
            fecha=date(2024, 1, 30),
            creado_por=gerente,
        )
        aprobar_gasto(gasto_viaje_guadalajara, gerente)

        gastos = [
            gasto_viaje_monterrey,
            gasto_papeleria,
            gasto_internet,
            gasto_marketing,
            gasto_nomina,
            gasto_renta,
            gasto_equipo,
            gasto_viaje_guadalajara,
        ]
        for gasto in gastos:
            self.stdout.write(
                f"Gasto creado: {gasto.titulo} ({gasto.get_estado_display()})"
            )

        return {
            "viaje_monterrey": gasto_viaje_monterrey,
            "papeleria": gasto_papeleria,
            "internet": gasto_internet,
            "marketing": gasto_marketing,
            "nomina": gasto_nomina,
            "renta": gasto_renta,
            "equipo": gasto_equipo,
            "viaje_guadalajara": gasto_viaje_guadalajara,
        }

    def _crear_pagos(self, usuarios, cuentas, gastos):
        contador = usuarios[f"{DEMO_USER_PREFIX}contador"]
        cuenta_principal, cuenta_operativa, cuenta_marketing = cuentas

        pagos = []

        # Pago PENDIENTE asociado al gasto de internet (APROBADO).
        pago_internet = crear_pago(
            gasto=gastos["internet"],
            cuenta=cuenta_marketing,
            monto=Decimal("1500.00"),
            fecha=date(2024, 2, 2),
            referencia="TRANSF-DEMO-001",
            notas="Pago pendiente de autorización.",
            user=contador,
        )
        pagos.append(pago_internet)

        # Pago APROBADO (sin efectuar) asociado al gasto de marketing.
        pago_marketing = crear_pago(
            gasto=gastos["marketing"],
            cuenta=cuenta_marketing,
            monto=Decimal("6000.00"),
            fecha=date(2024, 2, 6),
            referencia="TRANSF-DEMO-002",
            notas="Pago aprobado, pendiente de ejecución.",
            user=contador,
        )
        aprobar_pago(pago_marketing)
        pagos.append(pago_marketing)

        # Pago EFECTUADO que cubre por completo la nómina (gasto -> PAGADO).
        pago_nomina = crear_pago(
            gasto=gastos["nomina"],
            cuenta=cuenta_principal,
            monto=Decimal("10000.00"),
            fecha=date(2024, 2, 11),
            referencia="TRANSF-DEMO-003",
            notas="Pago de nómina efectuado.",
            user=contador,
        )
        aprobar_pago(pago_nomina)
        efectuar_pago(pago_nomina)
        pagos.append(pago_nomina)

        # Dos pagos EFECTUADOS que en conjunto cubren la renta (-> PAGADO).
        pago_renta_1 = crear_pago(
            gasto=gastos["renta"],
            cuenta=cuenta_operativa,
            monto=Decimal("5000.00"),
            fecha=date(2024, 2, 16),
            referencia="TRANSF-DEMO-004",
            notas="Primer abono de renta.",
            user=contador,
        )
        aprobar_pago(pago_renta_1)
        efectuar_pago(pago_renta_1)
        pagos.append(pago_renta_1)

        pago_renta_2 = crear_pago(
            gasto=gastos["renta"],
            cuenta=cuenta_operativa,
            monto=Decimal("3000.00"),
            fecha=date(2024, 2, 17),
            referencia="TRANSF-DEMO-005",
            notas="Segundo abono de renta.",
            user=contador,
        )
        aprobar_pago(pago_renta_2)
        efectuar_pago(pago_renta_2)
        pagos.append(pago_renta_2)

        # Pago CANCELADO asociado al viaje a Guadalajara, que luego se cancela.
        pago_viaje_guadalajara = crear_pago(
            gasto=gastos["viaje_guadalajara"],
            cuenta=cuenta_marketing,
            monto=Decimal("2200.00"),
            fecha=date(2024, 1, 31),
            referencia="TRANSF-DEMO-006",
            notas="Pago que finalmente se cancela.",
            user=contador,
        )
        cancelar_pago(pago_viaje_guadalajara)
        cancelar_gasto(gastos["viaje_guadalajara"], contador)
        pagos.append(pago_viaje_guadalajara)

        for pago in pagos:
            self.stdout.write(
                f"Pago creado: {pago} - {pago.monto} ({pago.get_estado_display()})"
            )

        return pagos
