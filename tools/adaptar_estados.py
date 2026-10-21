#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adapta el texto de las páginas de estado (/estados/<slug>/index.html) para
que cada una tenga su propio contenido y no sea un clon de otra.

Uso:
    python3 tools/adaptar_estados.py      # luego: python3 tools/generar_landings.py

Qué hace (solo texto; no toca estructura, clases, ids de secciones, botones,
menús ni scripts):
  - Corrige las páginas que eran copia de Cojedes (nombre del estado, ciudades,
    número de municipios y enlaces de WhatsApp).
  - Reescribe <title>, meta description, keywords, H1, subtítulo, títulos H2,
    introducciones de sección, lista de cobertura, ventajas, preguntas
    frecuentes, llamada a la acción, contacto y pie con redacciones
    distintas por estado y datos reales (capital, ciudades y municipios).
Es determinista: ejecutarlo varias veces produce el mismo resultado.
"""
import os
import re
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos import ESTADOS_INFO, ESTADOS_MUNICIPIOS, MUNICIPIOS  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDEN = sorted(ESTADOS_INFO)

# Ciudades de la plantilla de Cojedes que se copió en otras páginas
CLON = {"nombre": "Cojedes", "capital": "San Carlos",
        "ciudades": ["San Carlos", "Tinaquillo", "Cojeditos", "El Baúl", "Macapo", "El Pao"], "n": 9}


def municipios(slug):
    if slug == "carabobo":
        return [(m["nombre"], m["capital"]) for m in MUNICIPIOS]
    return ESTADOS_MUNICIPIOS[slug][1]


def nombre(slug):
    return "Carabobo" if slug == "carabobo" else ESTADOS_MUNICIPIOS[slug][0]


def v(pool, i, k=0):
    """Elige una variante distinta según el estado (i) y el bloque (k)."""
    return pool[(i * 3 + k * 5 + (i // 7) * (k + 2)) % len(pool)]


def lista_y(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " y " + items[-1]


# ---------------------------------------------------------------------------
# Variantes de redacción. {E}=estado, {C}=capital, {c2}..{c4}=otras ciudades,
# {N}=número de municipios
# ---------------------------------------------------------------------------
H1 = [
    'Trámites Legales en <span class="text-accent">{E} Venezuela</span> – SAREN, Registro Civil, Notarías y Más',
    'Abogados y Gestoría Legal en <span class="text-accent">{E} Venezuela</span>: SAREN, Registro Civil y Notarías',
    'Gestión de Trámites SAREN y Notariales en <span class="text-accent">{E} Venezuela</span>',
    'Abogados en <span class="text-accent">{E} Venezuela</span> para Trámites, Poderes y Documentos',
    'Tus Documentos Legales en <span class="text-accent">{E} Venezuela</span>, de Principio a Fin',
    'Asesoría Legal y Trámites en Línea en <span class="text-accent">{E} Venezuela</span>',
    'Registro Civil, SAREN y Notarías en <span class="text-accent">{E} Venezuela</span> con Abogados',
]
BADGE = ["Gestoría Legal Especializada", "Especialistas en Trámites Legales", "Abogados y Gestores",
         "Trámites SAREN y Notariales", "Asesoría Legal a Distancia", "Documentos Legales sin Filas",
         "Atención por WhatsApp"]
SUB = [
    "Gestionamos tus trámites legales en <strong>{E}</strong>: partidas y legalizaciones ante el <strong>SAREN</strong>, actas del <strong>Registro Civil</strong>, poderes y autenticaciones en <strong>notarías</strong>, y orientación para visas y pasaportes. Atendemos desde <strong>{C}</strong> hasta <strong>{c2}</strong> y el resto de los {N} municipios del estado.",
    "Si vives en <strong>{C}</strong>, <strong>{c2}</strong> o cualquier municipio de <strong>{E}</strong>, revisamos tus documentos y gestionamos tu trámite ante el <strong>SAREN</strong>, el <strong>Registro Civil</strong> o la <strong>notaría</strong> que corresponda, con seguimiento por WhatsApp.",
    "En <strong>{E}</strong> te ayudamos con lo que más se solicita: <strong>partidas de nacimiento</strong>, <strong>apostillas</strong>, <strong>poderes notariales</strong> y <strong>actas del Registro Civil</strong>. Trabajamos con clientes de <strong>{C}</strong>, <strong>{c3}</strong> y los {N} municipios del estado.",
    "Desde <strong>{C}</strong> hasta <strong>{c4}</strong>, atendemos a personas y empresas de <strong>{E}</strong> que necesitan resolver un trámite legal sin perder días en filas: <strong>SAREN</strong>, <strong>Registro Civil</strong>, <strong>notarías</strong> y solicitudes migratorias.",
    "Te acompañamos en tus trámites de <strong>{E}</strong> de principio a fin: revisamos los recaudos, preparamos los documentos y hacemos el seguimiento ante el <strong>SAREN</strong>, el <strong>Registro Civil</strong> y las <strong>notarías</strong> de <strong>{C}</strong> y el resto del estado.",
    "¿Eres de <strong>{E}</strong> y vives dentro o fuera de Venezuela? Gestionamos tus <strong>partidas</strong>, <strong>legalizaciones</strong>, <strong>poderes</strong> y <strong>actas</strong> con atención directa por WhatsApp, para <strong>{C}</strong>, <strong>{c2}</strong>, <strong>{c3}</strong> y todo el estado.",
    "Abogados y gestores para <strong>{E}</strong>: trámites ante el <strong>SAREN</strong>, el <strong>Registro Civil</strong> y las <strong>notarías</strong>, además de orientación para <strong>visas y pasaportes</strong>. Cobertura en los {N} municipios, con <strong>{C}</strong> como punto de partida.",
]
H2 = {
    "tramites-populares": [
        "Trámites Más Solicitados en {E}", "Lo Que Más Nos Piden en {E}", "Trámites Frecuentes en {E}",
        "Empieza Tu Trámite en {E}", "Gestiones Rápidas para {E}", "Elige Tu Trámite en {E}",
        "Los Trámites Más Comunes en {E}"],
    "servicios-integrales": [
        "Servicios Integrales de Trámites Legales en {E}", "Qué Gestionamos en {E}", "Servicios Legales Disponibles en {E}",
        "Cómo Te Ayudamos en {E}", "Nuestros Servicios para {E}", "Trámites que Gestionamos en {E}",
        "Servicios de Gestoría Legal en {E}"],
    "cobertura": [
        "Cobertura en Todo el Estado {E}", "Municipios de {E} Donde Atendemos", "Dónde Trabajamos en {E}",
        "Atención en los Municipios de {E}", "Cobertura Legal en {E}", "Llegamos a Todo {E}",
        "Zonas de {E} que Atendemos"],
    "lista-completa": [
        "Lista Completa de Trámites Disponibles en {E}", "Todos los Trámites que Puedes Hacer en {E}",
        "Catálogo de Trámites en {E}", "Trámites Disponibles para {E}", "Más Trámites en {E}",
        "Guía de Trámites en {E}", "Otros Trámites que Gestionamos en {E}"],
    "faq": [
        "Preguntas Frecuentes sobre Trámites en {E}", "Dudas Comunes sobre Trámites en {E}",
        "Lo Que Más Nos Preguntan en {E}", "Preguntas sobre Trámites Legales en {E}", "Resolvemos Tus Dudas en {E}",
        "Preguntas Frecuentes de Clientes de {E}", "Antes de Empezar Tu Trámite en {E}"],
    "contacto": [
        "Contáctenos para Trámites Legales en {E}", "Hablemos de Tu Trámite en {E}", "Escríbenos desde {E}",
        "Consulta Tu Caso en {E}", "Atención para Clientes de {E}", "Contacto para {E}", "Pide Tu Trámite en {E}"],
}
INTRO = {
    "tramites-populares": [
        "Haz clic en el trámite que necesitas para solicitar tu gestión inmediatamente",
        "Toca una opción y te escribimos por WhatsApp para empezar",
        "Selecciona el trámite y recibe orientación sobre los recaudos",
        "Elige una categoría para iniciar tu solicitud",
        "Los trámites que más gestionamos para clientes de {E}",
        "Empieza por el trámite que necesitas y te guiamos paso a paso",
        "Pide tu trámite con un solo clic"],
    "servicios-integrales": [
        "Gestión profesional de tus trámites legales en <strong>{C}</strong>, <strong>{c2}</strong> y todo el estado {E}",
        "Revisamos tus documentos antes de cada trámite para evitar rechazos en {E}",
        "Atención para <strong>{C}</strong>, <strong>{c3}</strong> y los demás municipios de {E}",
        "Cuatro áreas de trabajo para resolver tus trámites en {E}",
        "Trámites ante el SAREN, el Registro Civil y las notarías de {E}",
        "Desde <strong>{C}</strong> hasta <strong>{c4}</strong>, gestionamos tus documentos",
        "Servicios para personas y empresas de {E}"],
    "cobertura": [
        "Servicio profesional en los {N} municipios del estado {E}",
        "Atendemos los {N} municipios de {E} por WhatsApp y teléfono",
        "{N} municipios, una sola atención: la de tu abogado de confianza",
        "Trabajamos con clientes de los {N} municipios de {E}",
        "Cobertura en los {N} municipios del estado, con {C} como capital",
        "Los {N} municipios de {E} cuentan con nuestro servicio",
        "Gestionamos trámites para los {N} municipios de {E}"],
    "lista-completa": [
        "Más de 50 tipos de trámites legales que puedes gestionar en {E}",
        "Consulta la lista y escríbenos si tu trámite no aparece",
        "Trámites de SAREN, Registro Civil, notarías y documentos para el exterior",
        "Una guía rápida de lo que podemos gestionar para ti en {E}",
        "Si no ves tu trámite, pregúntanos por WhatsApp",
        "Organizados por tipo para que encuentres el tuyo",
        "Todos estos trámites se pueden iniciar a distancia"],
}
POR_QUE = [
    "En <strong class=\"text-primary\">Abogados Valencia</strong> trabajamos con clientes de todo el estado <strong>{E}</strong>: revisamos tus recaudos, preparamos los documentos y damos seguimiento a cada trámite ante el <strong>SAREN</strong>, el <strong>Registro Civil</strong> y las <strong>notarías</strong>.",
    "Los errores en un documento son la causa más común de retrasos. Por eso, en <strong class=\"text-primary\">Abogados Valencia</strong> revisamos cada trámite de <strong>{E}</strong> antes de presentarlo y te mantenemos informado de cada avance.",
    "Atendemos a personas de <strong>{C}</strong>, <strong>{c2}</strong> y el resto de <strong>{E}</strong>, también a quienes viven fuera del país y necesitan resolver un trámite en Venezuela con <strong class=\"text-primary\">Abogados Valencia</strong>.",
    "Con <strong class=\"text-primary\">Abogados Valencia</strong> tienes un abogado que te explica qué necesitas, cuánto cuesta y cuánto puede tardar tu trámite en <strong>{E}</strong>, antes de empezar.",
    "En <strong>{E}</strong> combinamos atención a distancia por WhatsApp con la gestión ante la oficina que corresponda. <strong class=\"text-primary\">Abogados Valencia</strong> se encarga del papeleo; tú solo apruebas cada paso.",
    "<strong class=\"text-primary\">Abogados Valencia</strong> gestiona trámites de <strong>SAREN</strong>, <strong>Registro Civil</strong>, <strong>notarías</strong> y solicitudes internacionales para clientes de los {N} municipios de <strong>{E}</strong>.",
    "Desde <strong>{C}</strong> hasta <strong>{c3}</strong>, en <strong class=\"text-primary\">Abogados Valencia</strong> te acompañamos con trámites claros, presupuesto por adelantado y seguimiento constante en <strong>{E}</strong>.",
]
POR_QUE_H2 = [
    '¿Por qué elegirnos para <span class="text-primary">tus trámites legales en {E}</span>?',
    '¿Por qué confiar tus trámites de <span class="text-primary">{E}</span> a nosotros?',
    'Así trabajamos tus <span class="text-primary">trámites en {E}</span>',
    'Tu abogado de confianza en <span class="text-primary">{E}</span>',
    'Qué ganas al gestionar <span class="text-primary">tus documentos de {E}</span> con nosotros',
    'Trámites en <span class="text-primary">{E}</span> sin complicaciones',
    'Un equipo legal para <span class="text-primary">todo {E}</span>',
]
VENTAJAS_T = ["Nuestras Ventajas en {E}", "Por Qué Confiar en Nosotros en {E}", "Lo Que Te Ofrecemos en {E}",
              "Ventajas para Clientes de {E}", "Qué Nos Diferencia en {E}", "Beneficios en {E}", "Así Trabajamos en {E}"]
VENTAJAS = [
    "<strong>Cobertura en los {N} municipios</strong> de {E}: {MUNS} y más",
    "<strong>SAREN {E}</strong>: partidas de nacimiento, apostillas y legalizaciones",
    "<strong>Registro Civil {E}</strong>: actas de nacimiento, matrimonio y defunción",
    "<strong>Notarías {E}</strong>: poderes, escrituras y autenticaciones",
    "<strong>Visas y pasaportes</strong>: orientación para trámites internacionales",
    "<strong>Revisión previa</strong> de recaudos para evitar rechazos",
    "<strong>Seguimiento constante</strong> por WhatsApp hasta la entrega",
]
FAQ = [
    [("¿Cómo solicito una partida de nacimiento del SAREN en {E}?",
      "Podemos gestionarla por ti. Envíanos por WhatsApp tus datos y los de la partida (nombre, fecha y lugar de registro) y nos encargamos de la solicitud y el seguimiento ante el <strong>SAREN</strong> hasta que el documento esté listo."),
     ("¿Pueden pedir mi partida de nacimiento de {C} si vivo fuera?",
      "Sí. Si tu partida está registrada en <strong>{C}</strong> u otro municipio de <strong>{E}</strong>, la solicitamos a distancia y te indicamos si necesitas legalizarla o apostillarla para usarla en el exterior."),
     ("¿Qué necesito para tramitar una partida en {E}?",
      "Normalmente basta con tu cédula y los datos del registro (nombres, fecha y municipio). Te confirmamos los recaudos exactos al revisar tu caso en <strong>{E}</strong>.")],
    [("¿Pueden ayudarme con la visa americana desde {E}?",
      "Te orientamos con la documentación, el formulario DS-160 y la preparación para la cita. La decisión sobre la visa corresponde exclusivamente al consulado."),
     ("¿Ayudan con pasaportes y trámites migratorios en {E}?",
      "Sí. Te orientamos sobre los requisitos del pasaporte venezolano y otros trámites migratorios, y preparamos los documentos de soporte que necesites desde <strong>{E}</strong>."),
     ("¿Gestionan documentos de {E} para usar en otro país?",
      "Sí. Te ayudamos con copias certificadas, legalización y la orientación para la apostilla de documentos emitidos en <strong>{E}</strong>.")],
    [("¿Ofrecen notaría virtual en {E}?",
      "Muchos pasos se adelantan a distancia: redacción del documento, revisión de datos y solicitud de la cita. Algunos actos notariales exigen la presencia del otorgante o de un apoderado, y te lo indicamos desde el principio."),
     ("¿Puedo otorgar un poder notarial en {E} sin estar en Venezuela?",
      "Depende del tipo de poder y del país donde estés. Te explicamos las opciones (consulado o apoderado en <strong>{E}</strong>) y redactamos el documento."),
     ("¿Qué documentos notariales gestionan en {C}?",
      "Poderes generales y especiales, autenticaciones, compraventas, declaraciones juradas y autorizaciones de viaje, entre otros, para <strong>{C}</strong> y el resto de <strong>{E}</strong>.")],
    [("¿Cuánto tardan los trámites del Registro Civil en {E}?",
      "Depende del tipo de acta, de la oficina y de la disponibilidad de citas. Te damos un estimado al revisar tu caso y te avisamos de cada avance."),
     ("¿Cuánto cuesta un trámite en {E}?",
      "Depende del trámite. Te informamos nuestros honorarios y las tasas oficiales antes de empezar, sin compromiso."),
     ("¿Atienden todos los municipios de {E}?",
      "Sí, atendemos los {N} municipios de <strong>{E}</strong>, desde <strong>{C}</strong> hasta <strong>{c2}</strong>, principalmente por WhatsApp y teléfono.")],
]
CTA_T = ["¡Solicita tus trámites legales en {E} hoy mismo!", "¿Listo para resolver tu trámite en {E}?",
         "Empieza hoy tu trámite en {E}", "Tu trámite en {E}, sin complicaciones",
         "Escríbenos y empieza tu trámite en {E}", "Resuelve tus documentos de {E} hoy",
         "Pide tu trámite en {E} por WhatsApp"]
CTA_P = [
    "SAREN, Registro Civil, notarías, visas y pasaportes. Atendemos {C}, {c2} y todo el estado {E}.",
    "Revisamos tus recaudos, preparamos el documento y te avisamos de cada avance. Cobertura en los {N} municipios de {E}.",
    "Desde {C} hasta {c3}: consulta tu caso por WhatsApp y recibe un presupuesto claro antes de empezar.",
    "Partidas, apostillas, poderes y actas para clientes de {E}, dentro y fuera de Venezuela.",
    "Te decimos qué necesitas, cuánto cuesta y cuánto puede tardar tu trámite en {E}.",
    "Atención directa por WhatsApp para {C}, {c4} y el resto de {E}.",
    "Gestión de trámites legales para los {N} municipios de {E}, con seguimiento hasta la entrega.",
]
CTA_S = ["Respuesta por WhatsApp • Cobertura en {N} municipios • Presupuesto previo",
         "Atención a distancia • {N} municipios de {E} • Seguimiento constante",
         "Consulta sin compromiso • Revisión de recaudos • {N} municipios",
         "WhatsApp y teléfono • Todo el estado {E} • Honorarios claros",
         "{N} municipios atendidos • Revisión previa • Seguimiento por WhatsApp",
         "Lunes a sábado • Cobertura en {E} • Atención personalizada",
         "Presupuesto antes de empezar • {N} municipios • Atención por WhatsApp"]
CONTACTO_P = [
    "¿Necesitas un trámite legal en <strong>{E} Venezuela</strong>? Escríbenos para consultas sobre <strong>SAREN</strong>, <strong>Registro Civil</strong>, <strong>notarías</strong>, <strong>visas</strong> o <strong>pasaportes</strong> en cualquier municipio del estado.",
    "Cuéntanos tu caso por WhatsApp y te respondemos con los recaudos y el presupuesto de tu trámite en <strong>{E}</strong>.",
    "Atendemos a clientes de <strong>{C}</strong>, <strong>{c2}</strong> y todo <strong>{E}</strong>. Escríbenos o llámanos en nuestro horario de atención.",
    "Para trámites en <strong>{E}</strong>, la forma más rápida de empezar es escribirnos por WhatsApp con una breve descripción de lo que necesitas.",
    "Si tienes dudas sobre un trámite en <strong>{E}</strong>, consúltanos sin compromiso: te orientamos antes de que inicies cualquier gestión.",
    "Desde <strong>{C}</strong> o desde el exterior, puedes iniciar tu trámite de <strong>{E}</strong> con nosotros por WhatsApp o teléfono.",
    "Escríbenos con el nombre del trámite y el municipio de <strong>{E}</strong> donde está registrado tu documento, y te indicamos los siguientes pasos.",
]
TITLE = [
    "Trámites Legales en {E} Venezuela – SAREN, Registro Civil y Notarías | Abogados Valencia",
    "Abogados en {E}: SAREN, Registro Civil, Notarías y Poderes | Abogados Valencia",
    "Gestoría Legal en {E} – Partidas, Apostillas y Poderes | Abogados Valencia",
    "Trámites SAREN y Notariales en {E}{CP} | Abogados Valencia",
    "Documentos Legales en {E}: Partidas, Actas y Legalizaciones | Abogados Valencia",
    "Abogados y Trámites en Línea en {E} Venezuela | Abogados Valencia",
    "Registro Civil, SAREN y Notarías en {E} | Abogados Valencia",
]
DESC = [
    "Trámites legales en {E}: SAREN, Registro Civil, notarías, poderes y apostillas. Atendemos {C}, {c2} y los {N} municipios por WhatsApp.",
    "Abogados para {E}: partidas de nacimiento, legalizaciones, poderes y actas en {C}, {c3} y todo el estado. Consulta por WhatsApp.",
    "Gestionamos tus trámites en {E} ante el SAREN, el Registro Civil y las notarías. {N} municipios atendidos, desde {C} hasta {c4}.",
    "¿Trámite en {E}? Partidas, apostillas, poderes notariales y actas en {C} y los {N} municipios. Presupuesto claro por WhatsApp.",
    "Trámites SAREN, Registro Civil y notarías en {E}: revisamos tus recaudos y damos seguimiento. Cobertura en {C}, {c2} y más.",
    "Abogados y gestores para {E} Venezuela: documentos legales, apostillas, poderes y visas. Atención a distancia en los {N} municipios.",
    "Partidas, actas, legalizaciones y poderes en {E} ({C}, {c3} y más). Abogados con atención por WhatsApp y teléfono.",
]
SERVICIOS_DISP = ["Trámites SAREN {c}", "Registro Civil {c}", "Notarías {c}", "Poderes notariales {c}",
                  "Apostillas {c}", "Servicios legales {c}"]
TARJETAS = [
    ["Gestión completa de trámites ante el Servicio Autónomo de Registros y Notarías en {E}.",
     "Partidas, legalizaciones y apostillas ante el SAREN para clientes de {C} y todo {E}.",
     "Preparamos y damos seguimiento a tus solicitudes del SAREN en {E}.",
     "Legalizaciones electrónicas, citas y documentos del SAREN para {E}.",
     "Revisamos tus recaudos antes de cada trámite del SAREN en {E}.",
     "Trámites del SAREN desde {C}, {c2} o desde el exterior.",
     "Tu trámite del SAREN en {E}, con seguimiento por WhatsApp."],
    ["Obtención de actas, certificados y documentos del Registro Civil en todo {E}.",
     "Actas de nacimiento, matrimonio y defunción registradas en {E}.",
     "Solicitamos tus actas del Registro Civil en {C} y el resto del estado.",
     "Certificaciones y copias del Registro Civil para usar dentro o fuera del país.",
     "Te ayudamos a ubicar y solicitar tu acta en el municipio de {E} donde se registró.",
     "Actas y certificados del Registro Civil de {E}, sin filas.",
     "Registro Civil de {E}: actas, certificados y correcciones."],
    ["Servicios notariales profesionales en {C} y todo el estado {E}.",
     "Poderes, autenticaciones y compraventas ante notarías de {E}.",
     "Redactamos tu documento y gestionamos la cita en la notaría de {E}.",
     "Documentos notariales para {C}, {c3} y el resto del estado.",
     "Poderes generales y especiales, declaraciones juradas y autorizaciones en {E}.",
     "Trámites notariales en {E} con revisión previa del documento.",
     "Notarías de {E}: te decimos qué recaudos llevar y te acompañamos."],
    ["Gestión de visas, pasaportes y otros trámites internacionales.",
     "Orientación para visas, pasaportes y trámites migratorios desde {E}.",
     "Documentos de soporte para visas y pasaportes de clientes de {E}.",
     "Te ayudamos a preparar tus solicitudes internacionales desde {C}.",
     "Visas, pasaportes y documentos para el exterior, paso a paso.",
     "Trámites migratorios y documentos internacionales para {E}.",
     "Solicitudes internacionales con orientación de abogados."],
]
PIE = [
    "Especialistas en trámites legales en {E} Venezuela: SAREN, Registro Civil, notarías, visas y pasaportes para {C} y los {N} municipios del estado.",
    "Gestoría legal para {E}: partidas, actas, poderes y apostillas, con atención por WhatsApp desde {C} hasta {c2}.",
    "Abogados y gestores para clientes de {E}, dentro y fuera de Venezuela. Trámites claros y seguimiento constante.",
    "Trámites de SAREN, Registro Civil y notarías para los {N} municipios de {E}, con presupuesto previo.",
    "Te ayudamos con tus documentos legales de {E}: revisión de recaudos, gestión y entrega.",
    "Atención legal a distancia para {C}, {c3} y todo el estado {E}.",
    "Documentos legales de {E} gestionados por abogados: partidas, legalizaciones, poderes y más.",
]
COPY = ("&copy; 2024 Abogados Valencia - Trámites legales en {E} Venezuela: SAREN, Registro Civil, notarías, "
        "visas y pasaportes en {CIUDADES} y los {N} municipios del estado.")


# ---------------------------------------------------------------------------
def rellenar(texto, ctx):
    return texto.format(**ctx)


def seccion(doc, sid):
    m = re.search(r'<section[^>]*id="%s"[^>]*>' % sid, doc)
    if not m:
        raise RuntimeError("sección %s no encontrada" % sid)
    fin = doc.index("</section>", m.end())
    return m.start(), fin


def en_seccion(doc, sid, patron, reemplazo, count=1, flags=re.S):
    a, b = seccion(doc, sid)
    parte, n = re.subn(patron, reemplazo, doc[a:b], count=count, flags=flags)
    if n == 0:
        raise RuntimeError("patrón no encontrado en %s: %s" % (sid, patron[:60]))
    return doc[:a] + parte + doc[b:]


def interno(etiqueta_regex, nuevo):
    """Reemplazo que conserva la etiqueta de apertura y cierre."""
    return lambda m: m.group(1) + nuevo + m.group(3)


def adaptar(slug, i):
    ruta = os.path.join(RAIZ, "estados", slug, "index.html")
    doc = original = open(ruta, encoding="utf-8").read()
    info = ESTADOS_INFO[slug]
    E = nombre(slug)
    muns = municipios(slug)
    ciudades = info["ciudades"] + [info["capital"]] * 4
    ctx = {"E": E, "C": info["capital"], "c2": ciudades[1], "c3": ciudades[2], "c4": ciudades[3], "N": len(muns),
           "MUNS": ", ".join(m for m, _ in muns[:7]),
           "CP": "" if info["capital"] == E else " (%s)" % info["capital"], "CIUDADES": lista_y(info["ciudades"][:4])}

    # 1) Páginas copiadas de Cojedes: nombre, ciudades y enlaces
    if slug != "cojedes" and "Cojedes" in doc:
        # El menú enlaza a todos los estados (incluido Cojedes): no se toca
        ini = doc.index("<!-- ========== MENÚ COMPLETO ========== -->")
        fin = doc.index("<!-- ========== FIN MENÚ ========== -->")
        menu = doc[ini:fin]
        doc = doc[:ini] + "\x00MENU\x00" + doc[fin:]
        doc = doc.replace('id="cobertura-cojedes"', 'id="cobertura-%s"' % slug)
        doc = re.sub(r'(href="https://wa\.me/[^"]*)"',
                     lambda m: m.group(1).replace("Cojedes", quote(E, safe="")) + '"', doc)
        for k, viejo in enumerate(CLON["ciudades"]):
            doc = doc.replace(viejo, ciudades[k])
        doc = doc.replace("%d municipios" % CLON["n"], "%d municipios" % len(muns))
        doc = doc.replace("Cojedes", E).replace("cojedes", E.lower())
        doc = doc.replace("\x00MENU\x00", menu)

    # 2) <title>, description y keywords
    titulo = rellenar(v(TITLE, i, 0), ctx)
    desc = rellenar(v(DESC, i, 1), ctx)
    kw = ", ".join([E.lower(), "abogados %s" % E.lower(), "trámites %s" % E.lower(), "saren %s" % E.lower(),
                    "registro civil %s" % E.lower(), "notarías %s" % E.lower()] +
                   ["abogado %s" % c.lower() for c in info["ciudades"][:4]] +
                   ["partida de nacimiento %s" % E.lower(), "apostilla %s" % E.lower(), "poder notarial %s" % E.lower()])
    doc = re.sub(r"<title>.*?</title>", "<title>%s</title>" % titulo, doc, count=1, flags=re.S)
    doc = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), doc, count=1)
    doc = re.sub(r'(<meta name="keywords" content=")[^"]*(")', lambda m: m.group(1) + kw + m.group(2), doc, count=1)

    # 3) Hero
    doc = en_seccion(doc, "inicio", r'(<span class="hero-badge">)(.*?)(</span>)', interno(None, v(BADGE, i, 2)))
    doc = en_seccion(doc, "inicio", r'(<h1 class="hero-title">)(.*?)(</h1>)', interno(None, rellenar(v(H1, i, 0), ctx)))
    doc = en_seccion(doc, "inicio", r'(<p class="hero-subtitle">)(.*?)(</p>)', interno(None, rellenar(v(SUB, i, 1), ctx)))

    # 4) Títulos H2 e introducciones de cada sección
    cob = re.search(r'id="(cobertura-[a-z-]+)"', doc).group(1)
    for clave, sid in (("tramites-populares", "tramites-populares"), ("servicios-integrales", "servicios-integrales"),
                       ("cobertura", cob), ("lista-completa", "lista-completa")):
        k = list(H2).index(clave)
        doc = en_seccion(doc, sid, r'(<h2 class="section-title"[^>]*>)(.*?)(</h2>)', interno(None, rellenar(v(H2[clave], i, k), ctx)))
        doc = en_seccion(doc, sid, r'(<p class="text-center mb-5"[^>]*>)(.*?)(</p>)', interno(None, rellenar(v(INTRO[clave], i, k), ctx)))
    doc = en_seccion(doc, "faq", r'(<h2 class="section-title"[^>]*>)(.*?)(</h2>)', interno(None, rellenar(v(H2["faq"], i, 4), ctx)))
    doc = en_seccion(doc, "contacto", r'(<h2 class="section-title"[^>]*>)(.*?)(</h2>)', interno(None, rellenar(v(H2["contacto"], i, 5), ctx)))

    # 5) Cobertura: municipios y servicios con datos reales
    lis_m = "\n".join('                            <li><strong>%s</strong> - %s</li>' % (m, c) for m, c in muns[:7])
    lis_s = "\n".join('                            <li><a href="#contacto">%s</a></li>' % (s.format(c=ciudades[k % len(info["ciudades"])]))
                      for k, s in enumerate(SERVICIOS_DISP))
    doc = en_seccion(doc, cob, r'(<i class="fas fa-map-marker-alt me-2"></i>)(.*?)(</h4>)', interno(None, " Principales Municipios de %s" % E))
    doc = en_seccion(doc, cob, r'(<ul class="service-features">)(.*?)(\s*</ul>)', interno(None, "\n" + lis_m), count=1)
    doc = en_seccion(doc, cob, r'(<i class="fas fa-globe me-2"></i>[^<]*</h4>\s*<ul class="service-features">)(.*?)(\s*</ul>)',
                     interno(None, "\n" + lis_s))

    # 6) ¿Por qué elegirnos? y ventajas
    doc = en_seccion(doc, "beneficios", r'(<h2 class="section-title text-start">)(.*?)(</h2>)',
                     interno(None, rellenar(v(POR_QUE_H2, i, 6), ctx)))
    doc = en_seccion(doc, "beneficios", r'(</h2>\s*<p>)(.*?)(</p>)', interno(None, rellenar(v(POR_QUE, i, 3), ctx)))
    doc = en_seccion(doc, "beneficios", r'(<i class="fas fa-check-circle me-2"></i>)(.*?)(</h4>)', interno(None, " " + rellenar(v(VENTAJAS_T, i, 4), ctx)))
    giro = i % len(VENTAJAS)
    orden = [VENTAJAS[0]] + VENTAJAS[1:][giro % 6:] + VENTAJAS[1:][:giro % 6]
    lis_v = "\n".join("                            <li>%s</li>" % rellenar(x, ctx) for x in orden)
    doc = en_seccion(doc, "beneficios", r'(<ul class="service-features">)(.*?)(\s*</ul>)', interno(None, "\n" + lis_v))

    # 7) Preguntas frecuentes (4 preguntas, variante distinta por estado)
    for n, alias in enumerate(("One", "Two", "Three", "Four")):
        q, r = FAQ[n][(i + n) % len(FAQ[n])]
        doc = en_seccion(doc, "faq", r'(data-bs-target="#collapse%s"[^>]*>\s*)(.*?)(\s*</button>)' % alias, interno(None, rellenar(q, ctx)))
        doc = en_seccion(doc, "faq", r'(<div id="collapse%s"[^>]*>\s*<div class="accordion-body">\s*)(.*?)(\s*</div>)' % alias,
                         interno(None, rellenar(r, ctx)))

    # 8) Llamada a la acción
    doc = en_seccion(doc, "cta", r'(<h2 class="cta-title">)(.*?)(</h2>)', interno(None, rellenar(v(CTA_T, i, 6), ctx)))
    doc = en_seccion(doc, "cta", r'(<p class="cta-subtitle">)(.*?)(</p>)', interno(None, rellenar(v(CTA_P, i, 0), ctx)))
    doc = en_seccion(doc, "cta", r'(<small class="text-light">)(.*?)(</small>)', interno(None, rellenar(v(CTA_S, i, 1), ctx)))

    # 9) Contacto y pie
    doc = en_seccion(doc, "contacto", r'(<p class="mb-4">)(.*?)(</p>)', interno(None, rellenar(v(CONTACTO_P, i, 2), ctx)))
    doc = en_seccion(doc, "contacto", r'(<h5>Cobertura [^<]*</h5>\s*<p>)(.*?)(</p>)', interno(None, "Servicio en los %d municipios del estado" % len(muns)))
    doc = en_seccion(doc, "contacto", r'(<h5>Cobertura [^<]*</h5>\s*<p>[^<]*</p>\s*<small class="text-muted">)(.*?)(</small>)',
                     interno(None, lista_y(info["ciudades"][:5]) + " y más"))
    doc = re.sub(r'(<div class="footer-bottom">\s*<p class="mb-0">)(.*?)(</p>)', interno(None, rellenar(COPY, ctx)), doc, count=1, flags=re.S)

    # 10) Descripción de las tarjetas de servicios y del pie
    for k, h3 in enumerate(("SAREN ", "Registro Civil ", "Notarías ", "Solicitudes Legales ")):
        doc = en_seccion(doc, "servicios-integrales",
                         r'(<h3 class="service-title">%s[^<]*</h3>\s*<p>)(.*?)(</p>)' % h3,
                         interno(None, rellenar(v(TARJETAS[k], i, k + 2), ctx)))
    doc = re.sub(r'(<div class="footer-logo">.*?</div>\s*<p class="mb-3">)(.*?)(</p>)',
                 interno(None, rellenar(v(PIE, i, 3), ctx)), doc, count=1, flags=re.S)

    if doc != original:
        open(ruta, "w", encoding="utf-8").write(doc)
        print("adaptado:", slug)


def main():
    for i, slug in enumerate(ORDEN):
        adaptar(slug, i)


if __name__ == "__main__":
    main()
