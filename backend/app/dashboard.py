from __future__ import annotations

from copy import deepcopy
from typing import Any

from .schemas import DashboardResponse
from .translator import LanguageCode, translate_text


BASE_DASHBOARD_CONTENT: dict[str, dict[str, Any]] = {
    "es": {
        "internal": {
            "badge": "Vista de operador",
            "eyebrow": "Control interno",
            "title": "Monitorea suscripciones, uso y riesgo comercial desde un solo panel.",
            "description": (
                "Este dashboard rapido nos deja revisar salud del negocio, cuentas activas "
                "y tareas previas al lanzamiento sin salir del producto."
            ),
            "stats": [
                {"label": "MRR", "value": "$24.8K", "delta": "+12.4%", "meta": "mensual", "tone": "teal"},
                {"label": "Suscripciones", "value": "184", "delta": "+17", "meta": "activas", "tone": "cyan"},
                {
                    "label": "Optimizaciones",
                    "value": "12.4K",
                    "delta": "+9%",
                    "meta": "ultimos 30 dias",
                    "tone": "sky",
                },
                {"label": "Expansion", "value": "8.2%", "delta": "3 upsells", "meta": "pipeline", "tone": "amber"},
            ],
            "spotlight": {
                "eyebrow": "Resumen operativo",
                "title": "La adopcion crece mas rapido en cuentas con onboarding guiado.",
                "description": (
                    "Las cuentas que activaron dos o mas espacios durante la primera semana "
                    "generaron mas optimizaciones, menor churn y renovaciones mas limpias."
                ),
                "bullets": [
                    "72% de las cuentas nuevas completaron el setup inicial.",
                    "8 clientes estan listos para migrar a plan Growth o Scale.",
                    "Facturacion y espacios compartidos siguen siendo el foco del lanzamiento.",
                ],
            },
            "board": {
                "eyebrow": "Prioridades",
                "title": "Tablero critico de esta semana",
                "items": [
                    {
                        "title": "Corregir banner de cuota agotada",
                        "meta": "Soporte · hoy",
                        "status": "En progreso",
                        "tone": "cyan",
                    },
                    {
                        "title": "Cerrar webhooks de billing",
                        "meta": "Backend · manana",
                        "status": "Bloqueante",
                        "tone": "coral",
                    },
                    {
                        "title": "Pulir dashboard cliente",
                        "meta": "Producto · viernes",
                        "status": "Listo para QA",
                        "tone": "teal",
                    },
                ],
            },
            "records": {
                "eyebrow": "Clientes recientes",
                "title": "Cuentas con mayor atencion",
                "rows": [
                    {
                        "name": "Northstar Labs",
                        "tier": "Scale",
                        "owner": "Marina",
                        "usage": "84% uso",
                        "status": "Saludable",
                    },
                    {
                        "name": "Aster Cloud",
                        "tier": "Growth",
                        "owner": "Pablo",
                        "usage": "Onboarding",
                        "status": "Seguimiento",
                    },
                    {
                        "name": "Lumen Ops",
                        "tier": "Pro",
                        "owner": "Carla",
                        "usage": "Renueva 02 Jun",
                        "status": "Estable",
                    },
                ],
            },
            "activity": {
                "eyebrow": "Actividad reciente",
                "title": "Lo ultimo del negocio",
                "items": [
                    {"title": "Nueva suscripcion desde Delta Studio", "meta": "Hace 12 min · Plan Growth"},
                    {"title": "Se agendo demo enterprise con Blue Canyon", "meta": "Hoy · 17:30"},
                    {
                        "title": "Northstar activo exportacion automatica",
                        "meta": "Hace 1 h · Workspace Reports",
                    },
                    {"title": "Se detecto pico de uso en cliente Beta", "meta": "Hace 2 h · Revisar creditos"},
                ],
            },
        },
        "client": {
            "badge": "Vista cliente",
            "eyebrow": "Portal del cliente",
            "title": "Da visibilidad inmediata del plan, uso y trabajo compartido.",
            "description": (
                "Es un dashboard simple para clientes suscritos: muestra estado de cuenta, "
                "espacios activos, creditos y movimientos recientes sin friccion."
            ),
            "stats": [
                {"label": "Plan", "value": "Scale", "delta": "Activo", "meta": "renovacion mensual", "tone": "teal"},
                {"label": "Seats", "value": "12 / 15", "delta": "3 libres", "meta": "equipo", "tone": "cyan"},
                {"label": "Creditos", "value": "72%", "delta": "8.4K restantes", "meta": "este ciclo", "tone": "sky"},
                {
                    "label": "Invoice",
                    "value": "14 May",
                    "delta": "Auto-pay",
                    "meta": "proxima factura",
                    "tone": "amber",
                },
            ],
            "spotlight": {
                "eyebrow": "Cuenta en marcha",
                "title": "Tu equipo ya tiene espacios y automatizaciones listos para trabajar.",
                "description": (
                    "La experiencia se centra en que el cliente entienda rapido si su cuenta "
                    "esta sana, cuanto le queda de uso y donde estan ocurriendo los resultados."
                ),
                "bullets": [
                    "3 workspaces activos con prompts compartidos.",
                    "Exportaciones programadas para reportes semanales.",
                    "Soporte prioritario y success manager asignado.",
                ],
            },
            "board": {
                "eyebrow": "Cuenta y soporte",
                "title": "Puntos clave del cliente",
                "items": [
                    {
                        "title": "Success manager asignada: Mariana",
                        "meta": "Respuesta objetivo < 2h",
                        "status": "Activo",
                        "tone": "teal",
                    },
                    {
                        "title": "Credito al 72% del ciclo",
                        "meta": "Recomendado: ampliar limite",
                        "status": "Atencion",
                        "tone": "amber",
                    },
                    {
                        "title": "Revision trimestral programada",
                        "meta": "En 6 dias · Meet confirmada",
                        "status": "Agendado",
                        "tone": "cyan",
                    },
                ],
            },
            "records": {
                "eyebrow": "Workspaces",
                "title": "Espacios del cliente",
                "rows": [
                    {
                        "name": "Sales Enablement",
                        "tier": "4 prompts",
                        "owner": "Ana",
                        "usage": "Editado hace 1 h",
                        "status": "Activo",
                    },
                    {
                        "name": "Client Reporting",
                        "tier": "12 automations",
                        "owner": "Luis",
                        "usage": "3 compartidos",
                        "status": "Estable",
                    },
                    {
                        "name": "Weekly Briefs",
                        "tier": "7 templates",
                        "owner": "Emma",
                        "usage": "Exporto hoy",
                        "status": "En uso",
                    },
                ],
            },
            "activity": {
                "eyebrow": "Actividad reciente",
                "title": "Movimiento de la cuenta",
                "items": [
                    {"title": "Se genero reporte para Acme", "meta": "Hace 18 min · Export PDF"},
                    {"title": "Nuevo teammate invitado al workspace", "meta": "Hoy · 2 seats consumidos"},
                    {"title": "Se actualizo prompt de onboarding", "meta": "Hace 54 min · Shared draft"},
                    {"title": "Alerta de uso al 70% enviada", "meta": "Hace 2 h · Billing notice"},
                ],
            },
        },
    },
    "en": {
        "internal": {
            "badge": "Operator view",
            "eyebrow": "Internal control",
            "title": "Monitor subscriptions, usage, and commercial risk from one place.",
            "description": (
                "This fast dashboard helps us review business health, active accounts, "
                "and launch tasks without leaving the product."
            ),
            "stats": [
                {"label": "MRR", "value": "$24.8K", "delta": "+12.4%", "meta": "monthly", "tone": "teal"},
                {"label": "Subscriptions", "value": "184", "delta": "+17", "meta": "active", "tone": "cyan"},
                {
                    "label": "Optimizations",
                    "value": "12.4K",
                    "delta": "+9%",
                    "meta": "last 30 days",
                    "tone": "sky",
                },
                {"label": "Expansion", "value": "8.2%", "delta": "3 upsells", "meta": "pipeline", "tone": "amber"},
            ],
            "spotlight": {
                "eyebrow": "Operations summary",
                "title": "Adoption is accelerating in guided-onboarding accounts.",
                "description": (
                    "Accounts that activated two or more workspaces in the first week "
                    "generated more optimizations, lower churn, and cleaner renewals."
                ),
                "bullets": [
                    "72% of new accounts completed the initial setup.",
                    "8 customers are ready to move into Growth or Scale.",
                    "Billing and shared workspaces are still the launch focus.",
                ],
            },
            "board": {
                "eyebrow": "Priorities",
                "title": "Critical board for this week",
                "items": [
                    {
                        "title": "Fix exhausted-quota banner",
                        "meta": "Support · today",
                        "status": "In progress",
                        "tone": "cyan",
                    },
                    {
                        "title": "Close billing webhooks",
                        "meta": "Backend · tomorrow",
                        "status": "Blocking",
                        "tone": "coral",
                    },
                    {
                        "title": "Polish client dashboard",
                        "meta": "Product · Friday",
                        "status": "Ready for QA",
                        "tone": "teal",
                    },
                ],
            },
            "records": {
                "eyebrow": "Recent customers",
                "title": "Accounts needing attention",
                "rows": [
                    {
                        "name": "Northstar Labs",
                        "tier": "Scale",
                        "owner": "Marina",
                        "usage": "84% usage",
                        "status": "Healthy",
                    },
                    {
                        "name": "Aster Cloud",
                        "tier": "Growth",
                        "owner": "Pablo",
                        "usage": "Onboarding",
                        "status": "Watchlist",
                    },
                    {
                        "name": "Lumen Ops",
                        "tier": "Pro",
                        "owner": "Carla",
                        "usage": "Renews Jun 02",
                        "status": "Stable",
                    },
                ],
            },
            "activity": {
                "eyebrow": "Recent activity",
                "title": "Latest business movement",
                "items": [
                    {"title": "New subscription from Delta Studio", "meta": "12 min ago · Growth plan"},
                    {"title": "Enterprise demo booked with Blue Canyon", "meta": "Today · 5:30 PM"},
                    {
                        "title": "Northstar enabled automated export",
                        "meta": "1 hour ago · Reports workspace",
                    },
                    {"title": "Usage spike detected on beta account", "meta": "2 hours ago · Review credits"},
                ],
            },
        },
        "client": {
            "badge": "Client view",
            "eyebrow": "Client portal",
            "title": "Give clients instant visibility into plan, usage, and shared work.",
            "description": (
                "This is a simple dashboard for subscribed customers: account health, "
                "workspaces, credits, and recent movement with minimal friction."
            ),
            "stats": [
                {"label": "Plan", "value": "Scale", "delta": "Active", "meta": "monthly renewal", "tone": "teal"},
                {"label": "Seats", "value": "12 / 15", "delta": "3 free", "meta": "team", "tone": "cyan"},
                {"label": "Credits", "value": "72%", "delta": "8.4K left", "meta": "this cycle", "tone": "sky"},
                {"label": "Invoice", "value": "May 14", "delta": "Auto-pay", "meta": "next invoice", "tone": "amber"},
            ],
            "spotlight": {
                "eyebrow": "Account in motion",
                "title": "Your team already has workspaces and automations ready to use.",
                "description": (
                    "The experience is centered on helping the client quickly understand "
                    "whether the account is healthy, how much usage is left, and where results happen."
                ),
                "bullets": [
                    "3 live workspaces with shared prompts.",
                    "Scheduled exports for weekly reporting.",
                    "Priority support and assigned success manager.",
                ],
            },
            "board": {
                "eyebrow": "Account and support",
                "title": "Key client points",
                "items": [
                    {
                        "title": "Assigned success manager: Mariana",
                        "meta": "Target response < 2h",
                        "status": "Active",
                        "tone": "teal",
                    },
                    {
                        "title": "Credits at 72% of cycle",
                        "meta": "Recommended: raise limit",
                        "status": "Attention",
                        "tone": "amber",
                    },
                    {
                        "title": "Quarterly review scheduled",
                        "meta": "In 6 days · Meet confirmed",
                        "status": "Scheduled",
                        "tone": "cyan",
                    },
                ],
            },
            "records": {
                "eyebrow": "Workspaces",
                "title": "Customer workspaces",
                "rows": [
                    {
                        "name": "Sales Enablement",
                        "tier": "4 prompts",
                        "owner": "Ana",
                        "usage": "Edited 1h ago",
                        "status": "Active",
                    },
                    {
                        "name": "Client Reporting",
                        "tier": "12 automations",
                        "owner": "Luis",
                        "usage": "3 shared",
                        "status": "Stable",
                    },
                    {
                        "name": "Weekly Briefs",
                        "tier": "7 templates",
                        "owner": "Emma",
                        "usage": "Exported today",
                        "status": "In use",
                    },
                ],
            },
            "activity": {
                "eyebrow": "Recent activity",
                "title": "Account movement",
                "items": [
                    {"title": "Report generated for Acme", "meta": "18 min ago · PDF export"},
                    {"title": "New teammate invited to workspace", "meta": "Today · 2 seats consumed"},
                    {"title": "Onboarding prompt updated", "meta": "54 min ago · Shared draft"},
                    {"title": "70% usage alert sent", "meta": "2 hours ago · Billing notice"},
                ],
            },
        },
    },
}


def _translate_view(view: dict[str, Any], target_language: LanguageCode) -> dict[str, Any]:
    translated_view = deepcopy(view)

    translated_view["badge"] = translate_text(view["badge"], target_language)
    translated_view["eyebrow"] = translate_text(view["eyebrow"], target_language)
    translated_view["title"] = translate_text(view["title"], target_language)
    translated_view["description"] = translate_text(view["description"], target_language)

    for stat, source_stat in zip(translated_view["stats"], view["stats"], strict=True):
        stat["label"] = translate_text(source_stat["label"], target_language)
        stat["meta"] = translate_text(source_stat["meta"], target_language)

    translated_view["spotlight"]["eyebrow"] = translate_text(view["spotlight"]["eyebrow"], target_language)
    translated_view["spotlight"]["title"] = translate_text(view["spotlight"]["title"], target_language)
    translated_view["spotlight"]["description"] = translate_text(
        view["spotlight"]["description"], target_language
    )
    translated_view["spotlight"]["bullets"] = [
        translate_text(bullet, target_language)
        for bullet in view["spotlight"]["bullets"]
    ]

    translated_view["board"]["eyebrow"] = translate_text(view["board"]["eyebrow"], target_language)
    translated_view["board"]["title"] = translate_text(view["board"]["title"], target_language)
    for item, source_item in zip(translated_view["board"]["items"], view["board"]["items"], strict=True):
        item["title"] = translate_text(source_item["title"], target_language)
        item["meta"] = translate_text(source_item["meta"], target_language)
        item["status"] = translate_text(source_item["status"], target_language)

    translated_view["records"]["eyebrow"] = translate_text(view["records"]["eyebrow"], target_language)
    translated_view["records"]["title"] = translate_text(view["records"]["title"], target_language)
    for row, source_row in zip(translated_view["records"]["rows"], view["records"]["rows"], strict=True):
        row["tier"] = translate_text(source_row["tier"], target_language)
        row["usage"] = translate_text(source_row["usage"], target_language)
        row["status"] = translate_text(source_row["status"], target_language)

    translated_view["activity"]["eyebrow"] = translate_text(view["activity"]["eyebrow"], target_language)
    translated_view["activity"]["title"] = translate_text(view["activity"]["title"], target_language)
    for item, source_item in zip(translated_view["activity"]["items"], view["activity"]["items"], strict=True):
        item["title"] = translate_text(source_item["title"], target_language)
        item["meta"] = translate_text(source_item["meta"], target_language)

    return translated_view


def get_dashboard_data(target_language: LanguageCode | None = None) -> DashboardResponse:
    safe_language = target_language or "es"
    if safe_language in BASE_DASHBOARD_CONTENT:
        selected_language = safe_language
        content = deepcopy(BASE_DASHBOARD_CONTENT[selected_language])
    else:
        source_content = BASE_DASHBOARD_CONTENT["en"]
        content = {
            audience: _translate_view(view, safe_language)
            for audience, view in source_content.items()
        }

    return DashboardResponse.model_validate(content)
