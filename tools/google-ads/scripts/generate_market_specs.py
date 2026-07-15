#!/usr/bin/env python3
"""Generate PAUSED EN/ES campaign specs from specs/markets.yaml.

The Bakersfield specifications are the approved copy/structure templates.
Market-specific strategy remains editable in YAML, not Python.
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "specs"
MATRIX_PATH = SPECS / "markets.yaml"

RSA_MAX_HEADLINES = 10
RSA_MAX_DESCRIPTIONS = 4


def _city_lc(city: str) -> str:
    return city.lower()


def _dedupe_keywords(keywords: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    cleaned: list[dict[str, Any]] = []
    for keyword in keywords:
        text = str(keyword.get("text", "")).strip()
        match_type = str(keyword.get("match_type", "PHRASE")).upper()
        if not text:
            continue
        key = (text.lower(), match_type)
        if key in seen:
            continue
        seen.add(key)
        cleaned.append({"text": text, "match_type": match_type})
    return cleaned


def _append_keywords(ad_group: dict[str, Any], additions: list[tuple[str, str]]) -> None:
    current = list(ad_group.get("keywords") or [])
    current.extend({"text": text, "match_type": match_type} for text, match_type in additions)
    ad_group["keywords"] = _dedupe_keywords(current)


def _add_exact_for_city_terms(ad_group: dict[str, Any], *, city: str, limit: int = 5) -> None:
    city_lower = _city_lc(city)
    keywords = list(ad_group.get("keywords") or [])
    existing = {
        (str(keyword.get("text", "")).strip().lower(), str(keyword.get("match_type", "")).upper())
        for keyword in keywords
    }
    added = 0
    for keyword in keywords:
        if str(keyword.get("match_type", "")).upper() != "PHRASE":
            continue
        text = str(keyword.get("text", "")).strip()
        if city_lower not in text.lower():
            continue
        key = (text.lower(), "EXACT")
        if key in existing:
            continue
        ad_group["keywords"].append({"text": text, "match_type": "EXACT"})
        existing.add(key)
        added += 1
        if added >= limit:
            break


def _fit_unique(values: list[str], *, max_count: int, max_len: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        key = text.lower()
        if not text or key in seen or len(text) > max_len:
            continue
        result.append(text)
        seen.add(key)
        if len(result) == max_count:
            break
    return result


def _set_rsa(
    ad_group: dict[str, Any],
    *,
    headlines: list[str],
    descriptions: list[str],
    path1: str,
    path2: str,
) -> None:
    ad_group["rsa"] = {
        "headlines": _fit_unique(headlines, max_count=RSA_MAX_HEADLINES, max_len=30),
        "descriptions": _fit_unique(descriptions, max_count=RSA_MAX_DESCRIPTIONS, max_len=90),
        "path1": path1[:15],
        "path2": path2[:15],
    }


def _campaign_assets(city: str, language: str) -> dict[str, Any]:
    if language == "es":
        return {
            "sitelinks": [
                ("Revisión de Caso", "Cuéntenos qué pasó.", "Consulta confidencial."),
                (
                    "Despido Injustificado",
                    "¿Cree que su despido fue injusto?",
                    "Hable con un abogado.",
                ),
                ("Discriminación Laboral", "Trato injusto laboral.", "Revise sus opciones."),
                ("Salarios y Horas", "¿Pago u horas extras?", "Aclare próximos pasos."),
                ("Represalias", "¿Represalias tras una queja?", "Proteja sus derechos."),
                ("Acoso Laboral", "Ambiente hostil o acoso.", "Ayuda confidencial."),
                ("Descansos y Comida", "¿Le negaron descansos?", "Revise su reclamo."),
                ("Consulta Gratis", "Sin compromiso inicial.", "Hablamos Español."),
            ],
            "callouts": [
                "Consulta Gratis",
                "Atención en Español",
                "Revisión Confidencial",
                "Representamos Empleados",
                f"Área de {city}",
                "Derechos del Empleado",
            ],
            "structured_snippets": [
                {
                    "header": "Tipos",
                    "values": [
                        "Despido Injustificado",
                        "Discriminación",
                        "Represalias",
                        "Acoso Laboral",
                        "Salarios y Horas",
                        "Descansos",
                    ],
                },
                {
                    "header": "Servicios",
                    "values": [
                        "Consulta Gratis",
                        "Revisión de Caso",
                        "Orientación Laboral",
                        "Ayuda en Español",
                    ],
                },
            ],
        }
    return {
        "sitelinks": [
            ("Free Case Review", "Tell us what happened.", "Confidential review."),
            ("Wrongful Termination", "Fired after reporting?", "Talk with a lawyer."),
            ("Discrimination Help", "Treated unfairly at work?", "Review your options."),
            ("Wage & Hour Claims", "Unpaid wages or overtime?", "Get clear guidance."),
            ("Retaliation Claims", "Punished for speaking up?", "Know your protections."),
            ("Harassment Help", "Hostile workplace issues?", "Confidential guidance."),
            ("Meal & Rest Breaks", "Missed breaks or lunches?", "Review possible claims."),
            ("Free Consultation", "No initial commitment.", "Hablamos Español."),
        ],
        "callouts": [
            "Free Consultation",
            "Employee-Side Counsel",
            "Confidential Review",
            "Hablamos Español",
            f"{city} Service Area",
            "California Employee Law",
            "Workplace Rights Review",
            "Employee Rights Guidance",
        ],
        "structured_snippets": [
            {
                "header": "Types",
                "values": [
                    "Wrongful Termination",
                    "Discrimination",
                    "Retaliation",
                    "Harassment",
                    "Wage & Hour",
                    "Meal Breaks",
                ],
            },
            {
                "header": "Services",
                "values": [
                    "Free Consultation",
                    "Case Review",
                    "Employee Rights",
                    "Legal Guidance",
                ],
            },
        ],
    }


def _en_ad_group_blueprints(city: str) -> list[dict[str, Any]]:
    city_lc = _city_lc(city)
    common_descriptions = [
        f"Employment Law Assist helps {city} employees understand possible legal options.",
        "Tell us what happened at work. Start with a free, confidential consultation.",
        "Employee-side guidance for wrongful firing, retaliation, harassment, and pay issues.",
        "Speak with an employment lawyer about your workplace concern and next steps.",
    ]
    return [
        {
            "name": "Employment Lawyer",
            "keywords": [
                (f"employment lawyer {city_lc}", "PHRASE"),
                (f"employment attorney {city_lc}", "PHRASE"),
                (f"{city_lc} employment lawyer", "PHRASE"),
                (f"{city_lc} employment attorney", "PHRASE"),
                (f"employment law attorney {city_lc}", "PHRASE"),
                (f"employment law lawyer {city_lc}", "PHRASE"),
                (f"labor lawyer {city_lc}", "PHRASE"),
                (f"labor attorney {city_lc}", "PHRASE"),
                (f"employee rights lawyer {city_lc}", "PHRASE"),
                (f"employee rights attorney {city_lc}", "PHRASE"),
                ("employment lawyer near me", "PHRASE"),
                ("employment attorney near me", "PHRASE"),
                ("employee rights lawyer near me", "PHRASE"),
                ("workplace lawyer near me", "PHRASE"),
            ],
            "headlines": [
                "Employment Lawyer Nearby",
                f"{city} Work Lawyer",
                f"{city} Job Attorney",
                "Employee Rights Guidance",
                "Talk With Counsel Today",
                "Employment Law Guidance",
                "Workplace Legal Help",
                "Confidential Case Review",
                "Fired or Treated Unfairly?",
                "California Employee Lawyer",
                "Get a Case Evaluation",
                "Protect Your Work Rights",
                "Experienced Work Counsel",
                "Free Employee Consultation",
                "Hablamos Español",
            ],
            "descriptions": common_descriptions,
            "path2": "Employment",
        },
        {
            "name": "Wrongful Termination",
            "keywords": [
                (f"wrongful termination lawyer {city_lc}", "PHRASE"),
                (f"wrongful termination attorney {city_lc}", "PHRASE"),
                (f"{city_lc} wrongful termination lawyer", "PHRASE"),
                (f"{city_lc} wrongful termination attorney", "PHRASE"),
                (f"wrongful firing lawyer {city_lc}", "PHRASE"),
                (f"wrongful firing attorney {city_lc}", "PHRASE"),
                (f"fired unfairly {city_lc}", "PHRASE"),
                ("wrongful termination lawyer near me", "PHRASE"),
                ("wrongful termination attorney near me", "PHRASE"),
                ("terminated without cause lawyer", "PHRASE"),
                ("fired after complaint lawyer", "PHRASE"),
            ],
            "headlines": [
                "Wrongful Termination Help",
                "Fired Unfairly at Work?",
                f"{city} Work Lawyer",
                f"{city} Firing Attorney",
                "Termination Case Review",
                "Talk About Your Firing",
                "Employee-Side Counsel",
                "Termination Law Guidance",
                "Know Your Work Rights",
                "Confidential Legal Review",
                "Get Guidance After Firing",
                "Free Termination Review",
                "Fired After Reporting?",
                "Retaliatory Firing Help",
                "California Employee Law",
            ],
            "descriptions": [
                "Think you were fired illegally? Learn what options may be available.",
                "Employment Law Assist reviews wrongful termination concerns for employees.",
                "Get clear next steps after a sudden, unfair, or retaliatory firing.",
                f"Guidance for {city} workers facing possible wrongful termination.",
            ],
            "path2": "Termination",
        },
        {
            "name": "Workplace Discrimination",
            "keywords": [
                (f"discrimination lawyer {city_lc}", "PHRASE"),
                (f"discrimination attorney {city_lc}", "PHRASE"),
                (f"workplace discrimination lawyer {city_lc}", "PHRASE"),
                (f"workplace discrimination attorney {city_lc}", "PHRASE"),
                (f"racial discrimination lawyer {city_lc}", "PHRASE"),
                (f"age discrimination attorney {city_lc}", "PHRASE"),
                ("workplace discrimination lawyer near me", "PHRASE"),
                ("workplace discrimination attorney near me", "PHRASE"),
                ("pregnancy discrimination lawyer", "PHRASE"),
            ],
            "headlines": [
                "Workplace Discrimination",
                "Treated Unfairly at Work?",
                "Discrimination Case Help",
                f"{city} Work Lawyer",
                f"{city} Bias Attorney",
                "Employee Rights Counsel",
                "Bias at Work? Talk Now",
                "Discrimination Law Help",
                "Confidential Case Review",
                "Protect Your Job Rights",
                "Get Legal Guidance Fast",
                "Age Discrimination Help",
                "Disability Bias Help",
                "Pregnancy Bias Claims",
                "Free Case Evaluation",
            ],
            "descriptions": [
                "Facing discrimination at work? Get a confidential review of what happened.",
                "We help employees explore options for workplace bias and unequal treatment.",
                f"Employment counsel for discrimination concerns affecting {city} workers.",
                "Start with a case evaluation and clear, practical next-step guidance.",
            ],
            "path2": "Bias",
        },
        {
            "name": "Workplace Retaliation",
            "keywords": [
                (f"retaliation lawyer {city_lc}", "PHRASE"),
                (f"retaliation attorney {city_lc}", "PHRASE"),
                (f"workplace retaliation lawyer {city_lc}", "PHRASE"),
                (f"workplace retaliation attorney {city_lc}", "PHRASE"),
                (f"fired after reporting {city_lc}", "PHRASE"),
                (f"whistleblower lawyer {city_lc}", "PHRASE"),
                ("workplace retaliation lawyer near me", "PHRASE"),
                ("workplace retaliation attorney near me", "PHRASE"),
                ("fired for reporting employer", "PHRASE"),
                ("retaliation after complaint", "PHRASE"),
                ("whistleblower retaliation lawyer", "PHRASE"),
            ],
            "headlines": [
                "Workplace Retaliation Help",
                "Punished for Speaking Up?",
                "Retaliation Case Review",
                f"{city} Work Lawyer",
                f"{city} Claim Attorney",
                "Employee Complaint Rights",
                "Fired After Reporting?",
                "Retaliation Legal Counsel",
                "Confidential Legal Help",
                "Know Your Protections",
                "Get a Case Evaluation",
                "Whistleblower Help",
                "Reported Issues at Work?",
                "Protected Activity Help",
                "Free Employee Review",
            ],
            "descriptions": [
                "Faced pushback after reporting issues at work? Talk with employment counsel.",
                "We help employees evaluate retaliation after complaints or protected activity.",
                f"Confidential guidance for {city} workers dealing with retaliation.",
                "Learn possible next steps with clear information and no pressure.",
            ],
            "path2": "Retaliation",
        },
        {
            "name": "Workplace Harassment",
            "keywords": [
                (f"harassment lawyer {city_lc}", "PHRASE"),
                (f"harassment attorney {city_lc}", "PHRASE"),
                (f"workplace harassment lawyer {city_lc}", "PHRASE"),
                (f"workplace harassment attorney {city_lc}", "PHRASE"),
                (f"sexual harassment lawyer {city_lc}", "PHRASE"),
                (f"sexual harassment attorney {city_lc}", "PHRASE"),
                (f"hostile work environment lawyer {city_lc}", "PHRASE"),
                ("workplace harassment lawyer near me", "PHRASE"),
                ("workplace harassment attorney near me", "PHRASE"),
                ("hostile work environment lawyer", "PHRASE"),
                ("employment harassment lawyer near me", "PHRASE"),
            ],
            "headlines": [
                "Workplace Harassment Help",
                "Hostile Work Environment?",
                "Harassment Case Review",
                f"{city} Work Lawyer",
                f"{city} Harassment Help",
                "Employee Safety Matters",
                "Sexual Harassment Help",
                "Employment Law Counsel",
                "Confidential Support",
                "Talk About What Happened",
                "Get Legal Guidance",
                "Free Harassment Review",
                "Unsafe Workplace?",
                "Hostile Job Conditions",
                "Employee Rights Matter",
            ],
            "descriptions": [
                "Dealing with harassment or a hostile workplace? Get confidential guidance.",
                "Employment Law Assist helps employees understand harassment-related options.",
                f"Legal support for {city} workers facing unsafe or hostile conditions.",
                "Start with a discreet case review and clear information.",
            ],
            "path2": "Harassment",
        },
        {
            "name": "Wage and Hour",
            "keywords": [
                (f"unpaid wages lawyer {city_lc}", "PHRASE"),
                (f"unpaid wages attorney {city_lc}", "PHRASE"),
                (f"overtime lawyer {city_lc}", "PHRASE"),
                (f"overtime attorney {city_lc}", "PHRASE"),
                (f"wage and hour lawyer {city_lc}", "PHRASE"),
                (f"wage and hour attorney {city_lc}", "PHRASE"),
                ("unpaid wages lawyer near me", "PHRASE"),
                ("unpaid overtime lawyer near me", "PHRASE"),
                ("unpaid overtime lawyer", "PHRASE"),
                ("missed meal break lawyer california", "PHRASE"),
                ("unpaid commission lawyer", "PHRASE"),
            ],
            "headlines": [
                "Wage & Hour Claim Help",
                "Unpaid Overtime Issues?",
                f"{city} Wage Lawyer",
                f"{city} Pay Attorney",
                "Missed Breaks or Pay?",
                "Employee Pay Rights",
                "Wage Claim Help",
                "Get a Pay Case Review",
                "Unpaid Wages Guidance",
                "California Wage Counsel",
                "Talk About Lost Pay",
                "Free Wage Claim Review",
                "Meal Break Violations?",
                "Unpaid Commissions?",
                "Overtime Pay Help",
            ],
            "descriptions": [
                "Missing wages, overtime, or breaks? Get clarity on possible next steps.",
                "Employment Law Assist helps employees with California wage-and-hour concerns.",
                f"Guidance for unpaid wage issues affecting {city} workers.",
                "Request a confidential review of your wage and hour situation.",
            ],
            "path2": "Wages",
        },
        {
            "name": "Meal and Rest Breaks",
            "keywords": [
                (f"meal break lawyer {city_lc}", "PHRASE"),
                (f"rest break attorney {city_lc}", "PHRASE"),
                (f"missed meal break lawyer {city_lc}", "PHRASE"),
                (f"missed rest break attorney {city_lc}", "PHRASE"),
                ("meal and rest break lawyer", "PHRASE"),
                ("california meal break lawyer", "PHRASE"),
                ("missed lunch break attorney", "PHRASE"),
                ("unpaid meal breaks lawyer", "PHRASE"),
            ],
            "headlines": [
                "Meal & Rest Break Help",
                "Missed Lunch Breaks?",
                f"{city} Break Lawyer",
                "California Break Rights",
                "Unpaid Break Time?",
                "Employee Pay Review",
                "Wage Claim Help",
                "Confidential Case Review",
                "Know Your Break Rights",
                "Talk With Work Counsel",
                "Free Break Claim Review",
                "Rest Break Violations?",
                "Meal Period Issues?",
                "Get Clear Guidance",
                "Protect Your Pay Rights",
            ],
            "descriptions": [
                "Missed meal or rest breaks can affect your pay. Ask for a confidential review.",
                "Get guidance on California break rules and possible wage-and-hour claims.",
                f"Employment Law Assist reviews break and pay issues for {city} employees.",
                "Tell us what happened and learn possible next steps for unpaid break time.",
            ],
            "path2": "Breaks",
        },
        {
            "name": "Medical Leave and Injury",
            "keywords": [
                (f"medical leave lawyer {city_lc}", "PHRASE"),
                (f"medical leave attorney {city_lc}", "PHRASE"),
                (f"fmla lawyer {city_lc}", "PHRASE"),
                (f"fired after medical leave {city_lc}", "PHRASE"),
                ("fired after injury lawyer", "PHRASE"),
                ("work injury retaliation lawyer", "PHRASE"),
                ("reasonable accommodation lawyer", "PHRASE"),
            ],
            "headlines": [
                "Medical Leave Job Help",
                "Fired After Leave?",
                f"{city} Leave Lawyer",
                "Disability Leave Rights",
                "Injured Worker Rights",
                "Accommodation Issues?",
                "Employee-Side Counsel",
                "Confidential Case Review",
                "Talk With Work Counsel",
                "Know Your Job Rights",
                "Free Leave Case Review",
                "Protected Leave Issues",
                "Retaliation After Injury?",
                "California Employee Help",
                "Get Clear Next Steps",
            ],
            "descriptions": [
                "Fired, punished, or denied accommodation after leave? Ask for a review.",
                "We help employees understand leave, injury, retaliation, and job-rights issues.",
                f"Confidential guidance for {city} employees after medical leave problems.",
                "Start with a free consultation and learn what options may apply.",
            ],
            "path2": "Leave",
        },
    ]


def _es_ad_group_blueprints(city: str) -> list[dict[str, Any]]:
    city_lc = _city_lc(city)
    common_descriptions = [
        f"Employment Law Assist ayuda a empleados en {city} a entender sus opciones.",
        "Cuéntenos qué pasó en el trabajo. Comience con una consulta confidencial gratis.",
        "Ayuda para despido, represalias, acoso, discriminación, salarios y descansos.",
        "Hable con un abogado laboral sobre su situación y posibles próximos pasos.",
    ]
    return [
        {
            "name": "Abogado Laboral",
            "keywords": [
                (f"abogado laboral {city_lc}", "PHRASE"),
                (f"abogado de trabajo {city_lc}", "PHRASE"),
                (f"abogado de empleo {city_lc}", "PHRASE"),
                (f"abogado derechos empleado {city_lc}", "PHRASE"),
                (f"abogado del trabajador {city_lc}", "PHRASE"),
                ("abogado laboral cerca de mi", "PHRASE"),
                ("abogado de trabajo cerca de mi", "PHRASE"),
                ("abogado derechos del empleado", "PHRASE"),
                ("abogado laboral california", "PHRASE"),
            ],
            "headlines": [
                "Abogado para Empleados",
                "Ayuda Legal en Trabajo",
                "Derechos del Empleado",
                "Consulta Confidencial",
                "Orientación Laboral",
                "Hable con un Abogado",
                "Casos de Empleo",
                "¿Problemas en Trabajo?",
                f"Abogado en {city}",
                "Revise Su Situación",
                "Apoyo Legal Laboral",
                "Empleados de California",
                "Consulta Gratis",
                "Despido o Maltrato?",
                "Se Habla Español",
            ],
            "descriptions": common_descriptions,
            "path2": "Laboral",
        },
        {
            "name": "Despido Injustificado",
            "keywords": [
                (f"abogado despido injustificado {city_lc}", "PHRASE"),
                (f"despido injustificado {city_lc}", "PHRASE"),
                (f"abogado por despido ilegal {city_lc}", "PHRASE"),
                (f"me despidieron injustamente {city_lc}", "PHRASE"),
                ("abogado despido injustificado", "PHRASE"),
                ("abogado por despido ilegal", "PHRASE"),
                ("terminacion ilegal del trabajo", "PHRASE"),
                ("me despidieron por quejarme", "PHRASE"),
            ],
            "headlines": [
                "Despido Injustificado",
                "¿Despido Injustificado?",
                "Abogado por Despido",
                "Revise Su Despido",
                "Ayuda por Despido",
                "Orientación Confidencial",
                "Derechos Tras Despido",
                f"Abogado en {city}",
                "Hable de Su Caso",
                "Evaluación del Caso",
                "Despido Tras Queja?",
                "Consulta Gratis",
                "Despido Ilegal?",
                "Empleado en California",
                "Siguientes Pasos Claros",
            ],
            "descriptions": [
                "¿Cree que su despido fue ilegal? Conozca qué opciones puede tener.",
                "Revisamos preocupaciones de despido injustificado para empleados.",
                "Pasos claros después de un despido súbito, injusto o en represalia.",
                f"Ayuda para trabajadores de {city} ante un posible despido injusto.",
            ],
            "path2": "Despido",
        },
        {
            "name": "Discriminación Laboral",
            "keywords": [
                (f"abogado discriminacion laboral {city_lc}", "PHRASE"),
                (f"discriminacion en el trabajo {city_lc}", "PHRASE"),
                (f"abogado discriminacion {city_lc}", "PHRASE"),
                (f"abogado discriminacion empleo {city_lc}", "PHRASE"),
                ("abogado discriminacion laboral", "PHRASE"),
                ("discriminacion racial trabajo", "PHRASE"),
                ("discriminacion por edad trabajo", "PHRASE"),
            ],
            "headlines": [
                "Discriminación Laboral",
                "¿Trato Injusto Trabajo?",
                "Ayuda por Discriminación",
                "Abogado para Empleados",
                "Derechos del Empleado",
                "Sesgo en el Empleo",
                "Consulta Confidencial",
                "Proteja Sus Derechos",
                "Orientación Legal Clara",
                "Casos de Discriminación",
                f"Ayuda en {city}",
                "Consulta Gratis",
                "Discapacidad o Edad?",
                "Trato Desigual?",
                "Abogado de Empleados",
            ],
            "descriptions": [
                "¿Enfrenta discriminación en el trabajo? Obtenga una revisión confidencial.",
                "Ayudamos a empleados a entender opciones ante sesgo o trato desigual.",
                f"Orientación laboral por discriminación para trabajadores de {city}.",
                "Comience con una evaluación clara y práctica de su situación.",
            ],
            "path2": "Sesgo",
        },
        {
            "name": "Represalias Laborales",
            "keywords": [
                (f"abogado represalias laborales {city_lc}", "PHRASE"),
                (f"represalias en el trabajo {city_lc}", "PHRASE"),
                (f"abogado represalia laboral {city_lc}", "PHRASE"),
                (f"me despidieron por reportar {city_lc}", "PHRASE"),
                ("abogado represalias laborales", "PHRASE"),
                ("represalia despues de queja", "PHRASE"),
                ("abogado denuncia laboral", "PHRASE"),
                ("me castigaron por quejarme", "PHRASE"),
            ],
            "headlines": [
                "Represalias en Trabajo",
                "¿Represalias por Quejarse?",
                "Ayuda por Represalias",
                "Abogado de Represalias",
                "Derechos al Denunciar",
                "¿Despido Tras Queja?",
                "Consulta Confidencial",
                "Conozca Sus Protecciones",
                "Revise Su Situación",
                "Orientación para Empleados",
                f"Ayuda en {city}",
                "Consulta Gratis",
                "Reportó un Problema?",
                "Proteja Sus Derechos",
                "Abogado de Empleados",
            ],
            "descriptions": [
                "¿Recibió represalias después de reportar un problema? Hable con abogados.",
                "Evaluamos represalias tras quejas o actividad protegida en el trabajo.",
                f"Orientación confidencial para trabajadores de {city}.",
                "Infórmese de posibles pasos sin presión ni promesas vacías.",
            ],
            "path2": "Represalia",
        },
        {
            "name": "Acoso Laboral",
            "keywords": [
                (f"abogado acoso laboral {city_lc}", "PHRASE"),
                (f"acoso en el trabajo {city_lc}", "PHRASE"),
                (f"acoso sexual en el trabajo {city_lc}", "PHRASE"),
                (f"abogado hostigamiento laboral {city_lc}", "PHRASE"),
                ("abogado acoso laboral", "PHRASE"),
                ("acoso sexual en el trabajo", "PHRASE"),
                ("ambiente hostil laboral", "PHRASE"),
                ("hostigamiento en el trabajo", "PHRASE"),
            ],
            "headlines": [
                "Acoso Laboral: Ayuda",
                "¿Ambiente Hostil?",
                "Revise un Caso de Acoso",
                "Abogado de Acoso Laboral",
                "Su Seguridad Importa",
                "Acoso Sexual Laboral",
                "Apoyo Confidencial",
                "Hable de lo Ocurrido",
                "Orientación Legal",
                f"Ayuda en {city}",
                "Consulta Gratis",
                "Hostigamiento Laboral",
                "Empleado Maltratado?",
                "Proteja Sus Derechos",
                "Abogado de Empleados",
            ],
            "descriptions": [
                "¿Sufre acoso o un ambiente hostil? Reciba orientación confidencial.",
                "Ayudamos a empleados a entender opciones ante hostigamiento laboral.",
                f"Apoyo legal para trabajadores de {city} ante acoso laboral.",
                "Comience con una revisión discreta y información clara.",
            ],
            "path2": "Acoso",
        },
        {
            "name": "Salarios y Horas",
            "keywords": [
                (f"abogado salarios no pagados {city_lc}", "PHRASE"),
                (f"abogado horas extras {city_lc}", "PHRASE"),
                (f"horas extras sin pagar {city_lc}", "PHRASE"),
                (f"abogado salario y horas {city_lc}", "PHRASE"),
                ("abogado salarios no pagados", "PHRASE"),
                ("horas extras sin pagar", "PHRASE"),
                ("no me pagan horas extras", "PHRASE"),
                ("descansos de comida california", "PHRASE"),
                ("abogado comisiones no pagadas", "PHRASE"),
            ],
            "headlines": [
                "Salarios y Horas Extra",
                "¿Horas Extra sin Pagar?",
                "Abogado de Salarios",
                "¿Descansos Omitidos?",
                "Derechos de Pago",
                "Ayuda por Salario",
                "Revise Su Pago",
                "Salarios Atrasados",
                "Orientación en CA",
                "Hable de Su Pago",
                f"Ayuda en {city}",
                "Consulta Gratis",
                "Comisiones No Pagadas?",
                "Pago Incompleto?",
                "Abogado de Empleados",
            ],
            "descriptions": [
                "¿Salarios, horas extra o descansos faltantes? Aclare posibles pasos.",
                "Ayudamos a empleados con problemas de salario y horas en California.",
                f"Orientación para trabajadores de {city} con salarios pendientes.",
                "Solicite una revisión confidencial de su situación de pago.",
            ],
            "path2": "Salarios",
        },
        {
            "name": "Descansos y Comida",
            "keywords": [
                (f"abogado descansos comida {city_lc}", "PHRASE"),
                (f"descanso de comida no pagado {city_lc}", "PHRASE"),
                (f"abogado descanso laboral {city_lc}", "PHRASE"),
                ("abogado descanso de comida", "PHRASE"),
                ("descansos y comida california", "PHRASE"),
                ("no me dan descansos trabajo", "PHRASE"),
                ("no me dan lunch en trabajo", "PHRASE"),
                ("descansos laborales no pagados", "PHRASE"),
            ],
            "headlines": [
                "Descansos y Comida",
                "¿Sin Lunch o Descanso?",
                "Ayuda por Descansos",
                "Derechos de Pago",
                "Abogado de Salarios",
                "Revise Su Reclamo",
                "Consulta Confidencial",
                "Orientación en CA",
                f"Ayuda en {city}",
                "Hable de Su Pago",
                "Consulta Gratis",
                "¿Descansos No Pagados?",
                "Comidas Omitidas?",
                "Derechos del Empleado",
                "Siguientes Pasos Claros",
            ],
            "descriptions": [
                "¿No le dieron comida o descanso? Revise si hay un reclamo de pago.",
                "Aclare reglas de descansos en California y posibles opciones laborales.",
                f"Ayuda confidencial para empleados de {city} con breaks o pagos faltantes.",
                "Cuéntenos qué pasó y reciba orientación inicial sin compromiso.",
            ],
            "path2": "Descansos",
        },
        {
            "name": "Licencia Médica",
            "keywords": [
                (f"abogado licencia medica {city_lc}", "PHRASE"),
                (f"despido por licencia medica {city_lc}", "PHRASE"),
                (f"me despidieron por enfermedad {city_lc}", "PHRASE"),
                ("abogado licencia medica", "PHRASE"),
                ("despido despues de lesion", "PHRASE"),
                ("represalia por lesion trabajo", "PHRASE"),
                ("acomodacion razonable trabajo", "PHRASE"),
            ],
            "headlines": [
                "Licencia Médica Laboral",
                "¿Despido Tras Licencia?",
                "Abogado de Licencia Médica",
                "Derechos por Discapacidad",
                "Lesión y Trabajo",
                "Acomodación Laboral",
                "Consulta Confidencial",
                "Revise Su Situación",
                f"Ayuda en {city}",
                "Proteja Sus Derechos",
                "Consulta Gratis",
                "Despido Tras Lesión?",
                "Derechos del Empleado",
                "Orientación en CA",
                "Siguientes Pasos Claros",
            ],
            "descriptions": [
                "¿Lo castigaron o despidieron tras licencia médica? Solicite una revisión.",
                "Ayudamos con licencia, discapacidad, represalias y derechos del empleado.",
                f"Orientación confidencial para empleados de {city} con problemas de licencia.",
                "Comience con una consulta gratis y conozca opciones posibles.",
            ],
            "path2": "Licencia",
        },
    ]


def _ensure_ad_groups(spec: dict[str, Any], *, city: str, language: str) -> None:
    blueprints = (
        _es_ad_group_blueprints(city)
        if language == "es"
        else _en_ad_group_blueprints(city)
    )
    by_name = {str(ad_group.get("name")): ad_group for ad_group in spec.get("ad_groups") or []}
    for blueprint in blueprints:
        ad_group = by_name.get(blueprint["name"])
        if ad_group is None:
            ad_group = {"name": blueprint["name"], "keywords": []}
            spec.setdefault("ad_groups", []).append(ad_group)
            by_name[blueprint["name"]] = ad_group
        ad_group["keywords"] = [
            {"text": text, "match_type": match_type}
            for text, match_type in blueprint["keywords"]
        ]
        _add_exact_for_city_terms(ad_group, city=city, limit=6)
        _set_rsa(
            ad_group,
            headlines=blueprint["headlines"],
            descriptions=blueprint["descriptions"],
            path1=city,
            path2=blueprint["path2"],
        )


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping: {path}")
    return data


def replace_text(value: Any, *, city: str, slug: str) -> Any:
    """Recursively replace Bakersfield template tokens."""
    if isinstance(value, str):
        return (
            value.replace("Bakersfield", city)
            .replace("bakersfield", slug)
            .replace("BAKERSFIELD", city.upper())
        )
    if isinstance(value, list):
        return [replace_text(item, city=city, slug=slug) for item in value]
    if isinstance(value, dict):
        return {
            key: replace_text(item, city=city, slug=slug)
            for key, item in value.items()
        }
    return value


def generate_spec(
    template: dict[str, Any],
    market: dict[str, Any],
    *,
    language: str,
    defaults: dict[str, Any],
) -> dict[str, Any]:
    city = str(market["city"])
    slug = str(market["slug"])
    spec = replace_text(copy.deepcopy(template), city=city, slug=slug)

    spec["name"] = f"ELA | Search | {city} | {language.upper()} | Nonbrand"
    spec["status"] = "PAUSED"
    spec["city"] = slug
    spec["language"] = language
    spec["geo_target_ids"] = list(market["geo_target_ids"])
    spec["geo_target_names"] = list(market["geo_target_names"])
    spec["location_presence_only"] = True
    spec["language_ids"] = [int(defaults["languages"][language])]
    spec["final_url"] = f"https://help.employmentlawassist.com/{slug}/{language}"
    spec["conversion_goals"] = [
        str(item) for item in defaults["conversion_action_ids"]
    ]

    assets = _campaign_assets(city, language)
    spec["callouts"] = assets["callouts"]
    spec["structured_snippets"] = assets["structured_snippets"]
    spec["sitelinks"] = [
        {
            "link_text": link_text,
            "final_url": spec["final_url"],
            "description1": description1,
            "description2": description2,
        }
        for link_text, description1, description2 in assets["sitelinks"]
    ]
    _ensure_ad_groups(spec, city=city, language=language)

    spec["market_metadata"] = {
        "priority": market["priority"],
        "landing_page_status": market["landing_page_status"],
        "geo_strategy": market["geo_strategy"],
        "service_area_notes": market["service_area_notes"],
        "overlap_group": market["overlap_group"],
        "do_not_launch_with": list(market.get("do_not_launch_with") or []),
        "generated_from": f"bakersfield-{language}.yaml",
        "launch_ready": market["landing_page_status"] == "active",
    }

    # Every ad group uses the market/language landing page.
    for ad_group in spec.get("ad_groups") or []:
        ad_group["final_url"] = spec["final_url"]
        _add_core_exact_variants(ad_group)
        _add_exact_for_city_terms(ad_group, city=city, limit=6)
        ad_group["keywords"] = _dedupe_keywords(list(ad_group.get("keywords") or []))

    # Every sitelink uses the market/language landing page until dedicated
    # practice-area routes are available.
    for sitelink in spec.get("sitelinks") or []:
        sitelink["final_url"] = spec["final_url"]

    tracking = spec.setdefault("tracking", {})
    tracking["final_url_suffix"] = (
        f"google_campaign=ela_search_{slug}_{language}_nonbrand"
        "&google_ad_group={_ad_group_name}&google_keyword={keyword}"
    )
    return spec


def _add_core_exact_variants(ad_group: dict[str, Any]) -> None:
    """Add exact variants for the first two high-intent phrase keywords."""
    keywords = list(ad_group.get("keywords") or [])
    existing = {
        (str(keyword.get("text", "")).strip().lower(), keyword.get("match_type"))
        for keyword in keywords
    }
    added = 0
    for keyword in keywords:
        if keyword.get("match_type") != "PHRASE":
            continue
        text = str(keyword.get("text", "")).strip()
        key = (text.lower(), "EXACT")
        if key in existing:
            continue
        ad_group["keywords"].append({"text": text, "match_type": "EXACT"})
        existing.add(key)
        added += 1
        if added == 2:
            break


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-bakersfield",
        action="store_true",
        help="Regenerate Bakersfield too (default preserves hand-edited source specs)",
    )
    args = parser.parse_args()

    matrix = load_yaml(MATRIX_PATH)
    templates = {
        language: load_yaml(SPECS / filename)
        for language, filename in matrix["base_templates"].items()
    }
    defaults = matrix["defaults"]

    generated = 0
    for market in matrix["markets"]:
        slug = market["slug"]
        if slug == "bakersfield" and not args.include_bakersfield:
            continue
        for language, template in templates.items():
            output = SPECS / f"{slug}-{language}.yaml"
            spec = generate_spec(
                template,
                market,
                language=language,
                defaults=defaults,
            )
            header = (
                f"# GENERATED from Bakersfield {language.upper()} template + markets.yaml\n"
                "# Review landing page and overlap metadata before launch.\n"
                "# Never hand-enable: campaign must be created PAUSED.\n\n"
            )
            output.write_text(
                header
                + yaml.safe_dump(
                    spec,
                    sort_keys=False,
                    allow_unicode=True,
                    width=120,
                ),
                encoding="utf-8",
            )
            print(f"Wrote {output.relative_to(ROOT)}")
            generated += 1

    print(f"Generated {generated} campaign specs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
