#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del sitio (solo AÑADE contenido; nunca borra lo existente).

Uso:
    python3 tools/generar_landings.py

Qué hace:
  1. Capa global en las páginas existentes (idempotente, entre marcadores
     <!-- AÑADIDO:... --> ... <!-- FIN AÑADIDO:... -->):
       - meta viewport-fit=cover, theme-color, iOS, iconos, manifest,
         Open Graph, Twitter Card, etiquetas geo y assets/css/ios.css
       - enlaces "SAREN en línea" y "Municipios" en el menú
       - barra inferior fija (Llamar / WhatsApp) y crédito del pie
       - en la portada: JSON-LD y secciones SAREN, zonas y municipios
  2. Landings /abogados/<municipio>/ y /abogados/<municipio>/<parroquia>/
     más el índice /abogados/ (datos en tools/datos.py)
  3. Landing /saren-en-linea/, 404.html, sitemap.xml, manifest.webmanifest,
     _headers y _redirects (solo para enlaces internos que ya existían y
     no tienen página, que hoy caen en la portada).
"""
import html
import json
import os
import re
import sys
import unicodedata
import zlib
from datetime import date
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos import (SITIO, MUNICIPIOS, ZONAS_CLAVE, SERVICIOS, SAREN_TRAMITES,  # noqa: E402
                   SAREN_RECAUDOS, SAREN_PASOS, SAREN_FAQ, INTROS_A, INTROS_B,
                   INTROS_C, FAQ_LOCAL, PASOS_LANDING)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOM = SITIO["dominio"].rstrip("/")
HOY = date.today().isoformat()
ESTADO = SITIO["estado"]
DESTACADO = SITIO["servicio_destacado"]
ORG_ID = DOM + "/#organization"
WEB_ID = DOM + "/#website"
LEGAL_ID = DOM + "/#legalservice"

e = html.escape


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def slugify(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t


def wa(msg):
    return "https://wa.me/%s?text=%s" % (SITIO["whatsapp"], quote(msg, safe=""))


def tel():
    return "tel:" + SITIO["telefono_e164"]


def elegir(lista, semilla, desplazamiento=0):
    return lista[(zlib.crc32(semilla.encode()) + desplazamiento) % len(lista)]


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def escribir(ruta, contenido):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)


def jsonld(obj):
    datos = json.dumps(obj, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return '<script type="application/ld+json">\n%s\n</script>' % datos


def bloque(nombre, contenido, sangria=""):
    return "%s<!-- AÑADIDO:%s -->\n%s\n%s<!-- FIN AÑADIDO:%s -->" % (
        sangria, nombre, contenido, sangria, nombre)


def poner_bloque(doc, nombre, contenido, ancla_regex, antes=True, sangria=""):
    """Inserta (o actualiza si ya existe) un bloque marcado. Nunca borra nada ajeno."""
    nuevo = bloque(nombre, contenido, sangria)
    patron = re.compile(r"[ \t]*<!-- AÑADIDO:%s -->.*?<!-- FIN AÑADIDO:%s -->" % (
        re.escape(nombre), re.escape(nombre)), re.S)
    if patron.search(doc):
        return patron.sub(lambda m: nuevo, doc, count=1)
    m = re.search(ancla_regex, doc, re.S)
    if not m:
        raise RuntimeError("No se encontró el ancla para el bloque %s" % nombre)
    if antes:
        pos = m.start()
        return doc[:pos] + nuevo + "\n" + doc[pos:]
    pos = m.end()
    return doc[:pos] + nuevo + "\n" + doc[pos:]


def municipio_por_slug(slug):
    for m in MUNICIPIOS:
        if m["slug"] == slug:
            return m
    raise KeyError(slug)


def url_mun(m):
    return "/abogados/%s/" % m["slug"]


def url_par(m, p):
    return "/abogados/%s/%s/" % (m["slug"], slugify(p))


# ---------------------------------------------------------------------------
# Fragmentos comunes
# ---------------------------------------------------------------------------
def head_extra(titulo, descripcion, canonical, lugar=None, tipo_og="website"):
    """Metaetiquetas añadidas (PWA, iOS, OG, Twitter, geo) y la capa iOS."""
    img = DOM + SITIO["imagen_og"]
    placename = lugar or "%s, %s" % (ESTADO, SITIO["pais"])
    lineas = [
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">',
        '<meta name="theme-color" content="%s">' % SITIO["theme_color"],
        '<meta name="apple-mobile-web-app-capable" content="yes">',
        '<meta name="mobile-web-app-capable" content="yes">',
        '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">',
        '<meta name="apple-mobile-web-app-title" content="%s">' % e(SITIO["nombre"]),
        '<meta name="format-detection" content="telephone=yes">',
        '<link rel="icon" href="/assets/icons/favicon.svg" type="image/svg+xml">',
        '<link rel="icon" href="/assets/icons/favicon-32.png" type="image/png" sizes="32x32">',
        '<link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png" sizes="180x180">',
        '<link rel="manifest" href="/manifest.webmanifest">',
        '<meta property="og:type" content="%s">' % tipo_og,
        '<meta property="og:locale" content="es_VE">',
        '<meta property="og:site_name" content="%s">' % e(SITIO["nombre"]),
        '<meta property="og:title" content="%s">' % e(titulo),
        '<meta property="og:description" content="%s">' % e(descripcion),
        '<meta property="og:url" content="%s">' % e(canonical),
        '<meta property="og:image" content="%s">' % e(img),
        '<meta property="og:image:width" content="498">',
        '<meta property="og:image:height" content="332">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % e(titulo),
        '<meta name="twitter:description" content="%s">' % e(descripcion),
        '<meta name="twitter:image" content="%s">' % e(img),
        '<meta name="geo.region" content="%s">' % SITIO["codigo_region"],
        '<meta name="geo.placename" content="%s">' % e(placename),
        '<link rel="stylesheet" href="/assets/css/ios.css">',
    ]
    return "\n".join("    " + l for l in lineas)


def cta_bar(msg):
    return (
        '    <nav class="cta-bar" aria-label="Contacto rápido">\n'
        '        <a href="%s" class="cta-call" aria-label="Llamar ahora al %s"><i class="fas fa-phone"></i> LLAMAR AHORA</a>\n'
        '        <a href="%s" class="cta-wa" target="_blank" rel="noopener" aria-label="Escribir por WhatsApp"><i class="fab fa-whatsapp"></i> WhatsApp</a>\n'
        '    </nav>' % (tel(), SITIO["telefono_visible"], e(wa(msg)))
    )


def credito():
    return (
        '    <div class="site-credit">%s · <a href="%s" target="_blank" rel="noopener">%s</a></div>'
        % (e(SITIO["credito_texto"]), SITIO["credito_enlace_url"], e(SITIO["credito_enlace_texto"]))
    )


MENU_DESKTOP = (
    '                <a href="/saren-en-linea/" class="nav-link">SAREN en línea</a>\n'
    '                <a href="/abogados/" class="nav-link">Municipios</a>'
)
MENU_MOVIL = (
    '        <a href="/saren-en-linea/" class="mobile-nav-link">SAREN en línea</a>\n'
    '        <a href="/abogados/" class="mobile-nav-link">Municipios</a>'
)


def organizacion():
    return {
        "@type": "Organization",
        "@id": ORG_ID,
        "name": SITIO["nombre"],
        "url": DOM + "/",
        "logo": DOM + SITIO["logo"],
        "telephone": SITIO["telefono_e164"],
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": SITIO["telefono_e164"],
            "contactType": "customer service",
            "areaServed": "VE",
            "availableLanguage": ["es"],
        },
    }


def sitio_web():
    return {
        "@type": "WebSite",
        "@id": WEB_ID,
        "url": DOM + "/",
        "name": SITIO["nombre"],
        "inLanguage": "es-VE",
        "publisher": {"@id": ORG_ID},
    }


def catalogo():
    return {
        "@type": "OfferCatalog",
        "name": "Servicios legales",
        "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["nombre"], "description": s["texto"]}}
            for s in SERVICIOS
        ],
    }


def horario():
    return [
        {"@type": "OpeningHoursSpecification", "dayOfWeek": h["dias"], "opens": h["abre"], "closes": h["cierra"]}
        for h in SITIO["horario"]
    ]


def lugar_estado():
    return {"@type": "AdministrativeArea", "name": "Estado %s" % ESTADO,
            "containedInPlace": {"@type": "Country", "name": SITIO["pais"]}}


def servicio_legal(area_served):
    return {
        "@type": "LegalService",
        "@id": LEGAL_ID,
        "name": SITIO["nombre"],
        "url": DOM + "/",
        "image": DOM + SITIO["logo"],
        "logo": DOM + SITIO["logo"],
        "telephone": SITIO["telefono_e164"],
        "parentOrganization": {"@id": ORG_ID},
        "address": {"@type": "PostalAddress", "addressRegion": ESTADO, "addressCountry": "VE"},
        "areaServed": area_served,
        "openingHoursSpecification": horario(),
        "hasOfferCatalog": catalogo(),
    }


def faq_ld(pares):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pares
        ],
    }


def migas_ld(migas):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": DOM + u}
            for i, (n, u) in enumerate(migas)
        ],
    }


def howto_ld(nombre, pasos):
    return {
        "@type": "HowTo",
        "name": nombre,
        "step": [
            {"@type": "HowToStep", "position": i + 1, "name": t, "text": d}
            for i, (t, d) in enumerate(pasos)
        ],
    }


# ---------------------------------------------------------------------------
# 1) Capa global sobre las páginas existentes
# ---------------------------------------------------------------------------
def paginas_existentes():
    res = []
    for base, dirs, archivos in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "tools", "abogados", "saren-en-linea", "assets")]
        if "index.html" in archivos:
            res.append(os.path.join(base, "index.html"))
    return sorted(res)


def meta(doc, nombre, attr="name"):
    m = re.search(r'<meta\s+%s="%s"\s+content="([^"]*)"' % (attr, re.escape(nombre)), doc)
    return html.unescape(m.group(1)) if m else ""


def titulo_doc(doc):
    m = re.search(r"<title>(.*?)</title>", doc, re.S)
    return html.unescape(m.group(1).strip()) if m else SITIO["nombre"]


def canonical_doc(doc):
    m = re.search(r'<link rel="canonical" href="([^"]+)"', doc)
    return m.group(1) if m else DOM + "/"


def faq_portada(doc):
    """Preguntas visibles del acordeón #faqAccordion de la portada."""
    seccion = re.search(r'id="faqAccordion">(.*?)</section>', doc, re.S).group(1)
    pares = []
    for q, a in re.findall(r'<button class="accordion-button[^"]*"[^>]*>\s*(.*?)\s*</button>.*?<div class="accordion-body">\s*(.*?)\s*</div>', seccion, re.S):
        limpio = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()
        pares.append((limpio(q), limpio(a)))
    return pares


def secciones_portada():
    tarjetas = []
    for slug_m, par in ZONAS_CLAVE:
        m = municipio_por_slug(slug_m)
        if par:
            nombre, url, sub = par, url_par(m, par), "Municipio %s" % m["nombre"]
        else:
            nombre, url, sub = m["capital"], url_mun(m), "Municipio %s" % m["nombre"]
        tarjetas.append(
            '                <div class="col-6 col-md-4 col-lg-3">\n'
            '                    <a class="zona-card" href="%s">\n'
            '                        <i class="fas fa-map-marker-alt"></i>\n'
            '                        <span class="zona-nombre">%s</span>\n'
            '                        <span class="zona-sub">%s</span>\n'
            '                    </a>\n'
            '                </div>' % (url, e(nombre), e(sub)))
    zonas = (
        '    <section class="py-5 home-zonas" id="zonas-carabobo">\n'
        '        <div class="container">\n'
        '            <h2 class="section-title">Zonas de %s donde trabajamos</h2>\n'
        '            <p class="text-center mb-4">Atendemos por WhatsApp y teléfono en todo el estado %s. Elige tu zona:</p>\n'
        '            <div class="row g-3">\n%s\n            </div>\n'
        '        </div>\n'
        '    </section>' % (e(ESTADO), e(ESTADO), "\n".join(tarjetas)))

    grupos = []
    for m in MUNICIPIOS:
        items = ['                        <a class="ios-row" href="%s"><strong>Municipio %s</strong></a>' % (url_mun(m), e(m["nombre"]))]
        for p in m["parroquias"]:
            items.append('                        <a class="ios-row" href="%s">Parroquia %s</a>' % (url_par(m, p), e(p)))
        grupos.append(
            '                <div class="col-md-6 col-lg-4">\n'
            '                    <p class="ios-group-title">%s</p>\n'
            '                    <div class="ios-group">\n%s\n                    </div>\n'
            '                </div>' % (e(m["nombre"]), "\n".join(items)))
    municipios = (
        '    <section class="py-5 home-municipios" id="municipios">\n'
        '        <div class="container">\n'
        '            <h2 class="section-title">Abogados en todos los municipios y parroquias de %s</h2>\n'
        '            <p class="text-center mb-4"><a href="/abogados/">Ver el índice completo de municipios</a></p>\n'
        '            <div class="row g-3">\n%s\n            </div>\n'
        '        </div>\n'
        '    </section>' % (e(ESTADO), "\n".join(grupos)))

    items_saren = "\n".join(
        '                        <li><i class="fas fa-check-circle"></i> %s</li>' % e(t) for t, _ in SAREN_TRAMITES[:6])
    saren = (
        '    <section class="home-saren py-5" id="saren-en-linea">\n'
        '        <div class="container">\n'
        '            <div class="saren-destacado">\n'
        '                <span class="badge-destacado">Servicio destacado</span>\n'
        '                <h2>SAREN en línea: te gestionamos el trámite</h2>\n'
        '                <p>Legalizaciones, autenticaciones, poderes, compraventas, registro de empresas y citas. Revisamos tus documentos antes de cargarlos para evitar rechazos.</p>\n'
        '                <ul class="saren-lista">\n%s\n                </ul>\n'
        '                <div class="saren-botones">\n'
        '                    <a href="/saren-en-linea/" class="btn btn-primary"><i class="fas fa-info-circle me-2"></i>Ver trámites y recaudos</a>\n'
        '                    <a href="%s" class="btn btn-success" target="_blank" rel="noopener"><i class="fab fa-whatsapp me-2"></i>Consultar por WhatsApp</a>\n'
        '                </div>\n'
        '                <p class="saren-aviso"><i class="fas fa-info-circle me-1"></i> Somos abogados y gestores independientes. No somos el SAREN ni una oficina oficial del Estado.</p>\n'
        '            </div>\n'
        '        </div>\n'
        '    </section>' % (items_saren, e(wa("Hola, vengo de la página web y necesito ayuda con un trámite de SAREN en línea"))))
    return saren, zonas, municipios


def jsonld_portada(doc):
    area = [lugar_estado()] + [
        {"@type": "City", "name": m["capital"],
         "containedInPlace": {"@type": "AdministrativeArea", "name": "Municipio %s, %s" % (m["nombre"], ESTADO)}}
        for m in MUNICIPIOS
    ]
    grafo = [organizacion(), sitio_web(), servicio_legal(area),
             {"@type": "Service", "name": DESTACADO, "serviceType": "Gestión de trámites ante registros y notarías",
              "provider": {"@id": LEGAL_ID}, "areaServed": lugar_estado(), "url": DOM + "/saren-en-linea/"},
             faq_ld(faq_portada(doc))]
    return jsonld({"@context": "https://schema.org", "@graph": grafo})


def mensaje_pagina(doc):
    t = re.split(r"\s[|–-]\s", titulo_doc(doc))[0].strip()
    return "Hola, vengo de la página web (%s) y necesito asesoría legal" % t


def aplicar_capa_global():
    for ruta in paginas_existentes():
        doc = leer(ruta)
        original = doc
        es_portada = os.path.abspath(ruta) == os.path.join(RAIZ, "index.html")
        titulo = titulo_doc(doc)
        descripcion = meta(doc, "description")
        canonical = canonical_doc(doc)
        cabecera = head_extra(titulo, descripcion, canonical,
                              lugar="Valencia, %s, %s" % (ESTADO, SITIO["pais"]) if es_portada else None)
        if es_portada:
            cabecera += '\n    <link rel="stylesheet" href="/assets/css/landings.css">'
            cabecera += "\n    " + jsonld_portada(doc).replace("\n", "\n    ")
        # Después de la hoja de estilos propia, para que ios.css cargue la última
        doc = poner_bloque(doc, "cabecera", cabecera, r'<link rel="stylesheet" href="styles.css">[ \t]*\n', antes=False, sangria="    ")
        doc = poner_bloque(doc, "menu-escritorio", MENU_DESKTOP, r"[ \t]*<!-- WhatsApp -->", sangria="                ")
        doc = poner_bloque(doc, "menu-movil", MENU_MOVIL, r"[ \t]*(<!-- WhatsApp Móvil -->\s*)?<div class=\"mobile-whatsapp\">", sangria="        ")
        if es_portada:
            saren, zonas, municipios = secciones_portada()
            doc = poner_bloque(doc, "portada-saren", saren, r"[ \t]*<!-- SECCIÓN INTEGRADA 1: GUÍA LEGAL", sangria="    ")
            doc = poner_bloque(doc, "portada-zonas", zonas + "\n\n" + municipios, r"[ \t]*<!-- About Section -->", sangria="    ")
        pie = cta_bar(mensaje_pagina(original)) + "\n" + credito()
        ancla = r"[ \t]*<!-- WA_PAGE_ID_SNIPPET -->" if "<!-- WA_PAGE_ID_SNIPPET -->" in doc else r"[ \t]*</body>"
        doc = poner_bloque(doc, "barra-inferior", pie, ancla, sangria="    ")
        if doc != original:
            escribir(ruta, doc)
            print("capa global:", os.path.relpath(ruta, RAIZ))


# ---------------------------------------------------------------------------
# 2) Plantilla de las páginas nuevas (mismo menú y pie que la portada)
# ---------------------------------------------------------------------------
def extraer_menu_y_pie():
    doc = leer(os.path.join(RAIZ, "index.html"))
    menu = re.search(r"[ \t]*<!-- ========== MENÚ COMPLETO ========== -->.*?<!-- ========== FIN MENÚ ========== -->", doc, re.S).group(0)
    pie = re.search(r"[ \t]*<!-- Footer -->\s*<footer>.*?</footer>", doc, re.S).group(0)
    snippet = re.search(r"<!-- WA_PAGE_ID_SNIPPET -->.*?</script>", doc, re.S).group(0)
    absolutos = lambda s: re.sub(r'href="#([^"]+)"', r'href="/#\1"', s)
    return absolutos(menu), absolutos(pie), snippet


MENU, PIE, SNIPPET_WA = None, None, None


def pagina(titulo, descripcion, ruta_url, cuerpo, grafo, msg_wa, lugar=None, h1_en_cuerpo=True):
    canonical = DOM + ruta_url
    ga = SITIO["ga_id"]
    return """<!DOCTYPE html>
<html lang="es-VE">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', '{ga}');
</script>

    <meta charset="UTF-8">
    <link rel="canonical" href="{canonical}">
    <meta name="description" content="{desc}">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <title>{titulo}</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <link rel="stylesheet" href="/styles.css">
{extra}
    <link rel="stylesheet" href="/assets/css/landings.css">
    {ld}
</head>
<body class="lp">
{menu}

    <main id="contenido">
{cuerpo}
    </main>

{pie}

{barra}
{credito}

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script src="/script.js"></script>

{snippet}
</body>
</html>
""".format(ga=ga, canonical=e(canonical), desc=e(descripcion), titulo=e(titulo),
           extra=head_extra(titulo, descripcion, canonical, lugar=lugar),
           ld=jsonld({"@context": "https://schema.org", "@graph": grafo}).replace("\n", "\n    "),
           menu=MENU, cuerpo=cuerpo, pie=PIE, barra=cta_bar(msg_wa), credito=credito(), snippet=SNIPPET_WA)


def html_migas(migas):
    partes = []
    for i, (n, u) in enumerate(migas):
        if i == len(migas) - 1:
            partes.append('<li class="breadcrumb-item active" aria-current="page">%s</li>' % e(n))
        else:
            partes.append('<li class="breadcrumb-item"><a href="%s">%s</a></li>' % (u, e(n)))
    return ('        <nav aria-label="Ruta de navegación" class="lp-migas">\n'
            '            <div class="container"><ol class="breadcrumb mb-0">%s</ol></div>\n'
            '        </nav>' % "".join(partes))


def html_pasos(pasos, titulo):
    items = "\n".join(
        '                <div class="col-sm-6 col-lg-%d"><div class="lp-paso"><span class="lp-num">%d</span><h3>%s</h3><p>%s</p></div></div>'
        % (12 // min(len(pasos), 4) if len(pasos) <= 4 else 4, i + 1, e(t), e(d)) for i, (t, d) in enumerate(pasos))
    return ('        <section class="lp-seccion lp-gris">\n            <div class="container">\n'
            '                <h2 class="lp-h2">%s</h2>\n                <div class="row g-3">\n%s\n                </div>\n'
            '            </div>\n        </section>' % (e(titulo), items))


def html_faq(pares, titulo):
    items = "\n".join(
        '                    <details class="lp-faq-item"%s><summary>%s</summary><p>%s</p></details>'
        % (" open" if i == 0 else "", e(q), e(a)) for i, (q, a) in enumerate(pares))
    return ('        <section class="lp-seccion">\n            <div class="container lp-estrecho">\n'
            '                <h2 class="lp-h2">%s</h2>\n                <div class="lp-faq">\n%s\n                </div>\n'
            '            </div>\n        </section>' % (e(titulo), items))


def html_saren_bloque(lugar):
    lis = "\n".join('                        <li><i class="fas fa-check-circle"></i> %s</li>' % e(t) for t, _ in SAREN_TRAMITES[:6])
    return (
        '        <section class="lp-seccion">\n            <div class="container">\n'
        '                <div class="saren-destacado">\n'
        '                    <span class="badge-destacado">Servicio destacado</span>\n'
        '                    <h2>%s en %s</h2>\n'
        '                    <p>Te ayudamos a preparar, cargar y dar seguimiento a tus trámites ante registros y notarías, con revisión previa de los recaudos para evitar rechazos.</p>\n'
        '                    <ul class="saren-lista">\n%s\n                    </ul>\n'
        '                    <div class="saren-botones">\n'
        '                        <a href="%s" class="btn btn-success" target="_blank" rel="noopener"><i class="fab fa-whatsapp me-2"></i>Pedir %s en %s</a>\n'
        '                        <a href="/saren-en-linea/" class="btn btn-primary"><i class="fas fa-list-check me-2"></i>Trámites y recaudos</a>\n'
        '                    </div>\n'
        '                    <p class="saren-aviso"><i class="fas fa-info-circle me-1"></i> Somos abogados y gestores independientes. No somos el SAREN ni una oficina oficial del Estado.</p>\n'
        '                </div>\n'
        '            </div>\n        </section>'
        % (e(DESTACADO), e(lugar), lis, e(wa("Hola, necesito un trámite de %s en %s" % (DESTACADO, lugar))), e(DESTACADO), e(lugar)))


def html_servicios(lugar, municipio, semilla):
    rot = zlib.crc32(semilla.encode()) % (len(SERVICIOS) - 1)
    resto = SERVICIOS[1:]
    orden = [SERVICIOS[0]] + resto[rot:] + resto[:rot]
    tarjetas = []
    for s in orden:
        mas = ('<a href="%s" class="lp-mas">Más información</a>' % s["url"]) if s["url"] else ""
        msg = "Hola, necesito asesoría de %s en %s, Municipio %s" % (s["nombre"].lower(), lugar, municipio)
        tarjetas.append(
            '                    <div class="col-md-6 col-lg-4">\n'
            '                        <div class="lp-servicio">\n'
            '                            <div class="lp-servicio-icono"><i class="fas %s"></i></div>\n'
            '                            <h3>%s en %s</h3>\n'
            '                            <p>%s</p>\n'
            '                            <div class="lp-servicio-acciones">\n'
            '                                <a href="%s" class="btn btn-success btn-sm" target="_blank" rel="noopener"><i class="fab fa-whatsapp me-1"></i>Consultar por WhatsApp</a>\n'
            '                                %s\n'
            '                            </div>\n'
            '                        </div>\n'
            '                    </div>' % (s["icono"], e(s["nombre"]), e(lugar), e(s["texto"]), e(wa(msg)), mas))
    return ('        <section class="lp-seccion lp-gris" id="servicios-lugar">\n            <div class="container">\n'
            '                <h2 class="lp-h2">Servicios legales en %s</h2>\n'
            '                <div class="row g-3">\n%s\n                </div>\n'
            '            </div>\n        </section>' % (e(lugar), "\n".join(tarjetas)))


def html_enlaces(m, actual_parroquia=None):
    cercanas = []
    for p in m["parroquias"]:
        if p != actual_parroquia:
            cercanas.append((url_par(m, p), "Parroquia %s" % p, "Municipio %s" % m["nombre"]))
    for v in m["vecinos"]:
        vm = municipio_por_slug(v)
        for p in vm["parroquias"][:3]:
            cercanas.append((url_par(vm, p), "Parroquia %s" % p, "Municipio %s" % vm["nombre"]))
    filas_c = "\n".join(
        '                        <a class="ios-row" href="%s"><span>%s<small>%s</small></span></a>' % (u, e(n), e(s))
        for u, n, s in cercanas)
    otros = [x for x in MUNICIPIOS if x["slug"] != m["slug"]]
    filas_m = "\n".join(
        '                        <a class="ios-row" href="%s"><span>Municipio %s<small>%s</small></span></a>'
        % (url_mun(x), e(x["nombre"]), e(x["capital"])) for x in otros)
    volver = ""
    if actual_parroquia:
        volver = ('                <p class="mt-3"><a href="%s"><i class="fas fa-arrow-left me-1"></i>Volver al municipio %s</a></p>\n'
                  % (url_mun(m), e(m["nombre"])))
    return ('        <section class="lp-seccion">\n            <div class="container">\n'
            '                <div class="row g-4">\n'
            '                    <div class="col-lg-6">\n'
            '                    <h2 class="lp-h2 text-start">Parroquias y zonas cercanas</h2>\n'
            '                    <div class="ios-group">\n%s\n                    </div>\n'
            '                    </div>\n'
            '                    <div class="col-lg-6">\n'
            '                    <h2 class="lp-h2 text-start">Otros municipios de %s</h2>\n'
            '                    <div class="ios-group">\n%s\n                    </div>\n'
            '                    </div>\n'
            '                </div>\n%s'
            '            </div>\n        </section>' % (filas_c, e(ESTADO), filas_m, volver))


def html_cta_final(lugar):
    return ('        <section class="lp-cta-final">\n            <div class="container text-center">\n'
            '                <h2>¿Necesitas un abogado en %s?</h2>\n'
            '                <p>Escríbenos ahora y recibe orientación sobre tu caso o trámite. Horario: %s</p>\n'
            '                <div class="lp-botones justify-content-center">\n'
            '                    <a href="%s" class="btn btn-success btn-lg" target="_blank" rel="noopener"><i class="fab fa-whatsapp me-2"></i>Escribir por WhatsApp</a>\n'
            '                    <a href="%s" class="btn btn-danger btn-lg"><i class="fas fa-phone me-2"></i>Llamar al %s</a>\n'
            '                </div>\n'
            '            </div>\n        </section>'
            % (e(lugar), e(SITIO["horario_texto"][0].lower() + SITIO["horario_texto"][1:]),
               e(wa("Hola, necesito un abogado en %s" % lugar)), tel(), e(SITIO["telefono_local"])))


def landing(m, parroquia=None):
    es_parroquia = parroquia is not None
    lugar = parroquia if es_parroquia else m["capital"]
    ruta = url_par(m, parroquia) if es_parroquia else url_mun(m)
    semilla = ruta
    h1 = "Abogado en %s, Municipio %s" % (lugar, m["nombre"])
    if es_parroquia:
        titulo = "%s | Parroquia %s, %s" % (h1, parroquia, ESTADO)
        desc = ("Abogado en la parroquia %s, municipio %s (%s): %s, documentos, contratos, divorcios y herencias. "
                "Atención por WhatsApp y teléfono." % (parroquia, m["nombre"], ESTADO, DESTACADO))
    else:
        titulo = "%s | Abogados en %s" % (h1, ESTADO)
        desc = ("Abogado en %s, municipio %s, estado %s: %s, registros y notarías, contratos, divorcios y herencias. "
                "Consulta por WhatsApp." % (lugar, m["nombre"], ESTADO, DESTACADO))
    vars_ = dict(lugar=lugar, municipio=m["nombre"], capital=m["capital"], zona=m["zona"], estado=ESTADO, servicio=DESTACADO)
    intro = [elegir(INTROS_A, semilla).format(**vars_),
             elegir(INTROS_B, semilla, 3).format(**vars_),
             elegir(INTROS_C, semilla, 5).format(**vars_)]
    inicio = zlib.crc32(semilla.encode()) % len(FAQ_LOCAL)
    faqs = [(q.format(**vars_), a.format(**vars_)) for q, a in (FAQ_LOCAL[inicio:] + FAQ_LOCAL[:inicio])[:4]]

    migas = [("Inicio", "/"), ("Abogados en %s" % ESTADO, "/abogados/"), ("Municipio %s" % m["nombre"], url_mun(m))]
    if es_parroquia:
        migas.append(("Parroquia %s" % parroquia, ruta))

    if es_parroquia:
        place = {"@type": "Place", "name": "Parroquia %s" % parroquia,
                 "containedInPlace": {"@type": "AdministrativeArea", "name": "Municipio %s" % m["nombre"],
                                      "containedInPlace": lugar_estado()}}
    else:
        place = {"@type": "AdministrativeArea", "name": "Municipio %s" % m["nombre"],
                 "containedInPlace": lugar_estado()}
    grafo = [
        {"@type": "WebPage", "@id": DOM + ruta + "#webpage", "url": DOM + ruta, "name": titulo,
         "description": desc, "inLanguage": "es-VE", "isPartOf": {"@id": WEB_ID},
         "breadcrumb": {"@id": DOM + ruta + "#breadcrumb"}},
        organizacion(),
        servicio_legal(place),
        {"@type": "Service", "name": "%s en %s" % (DESTACADO, lugar),
         "serviceType": "Gestión de trámites ante registros y notarías",
         "provider": {"@id": LEGAL_ID}, "areaServed": place, "url": DOM + ruta},
        dict(migas_ld(migas), **{"@id": DOM + ruta + "#breadcrumb"}),
        faq_ld(faqs),
        howto_ld("Cómo contratar un abogado en %s" % lugar, PASOS_LANDING),
    ]

    cuerpo = "\n\n".join([
        html_migas(migas),
        '        <header class="lp-hero">\n            <div class="container">\n'
        '                <span class="lp-etiqueta"><i class="fas fa-map-marker-alt me-1"></i> %s · Municipio %s · %s</span>\n'
        '                <h1>%s</h1>\n'
        '                <p class="lp-lead">%s</p>\n'
        '                <p>%s %s</p>\n'
        '                <div class="lp-botones">\n'
        '                    <a href="%s" class="btn btn-success btn-lg" target="_blank" rel="noopener"><i class="fab fa-whatsapp me-2"></i>Consultar por WhatsApp</a>\n'
        '                    <a href="%s" class="btn btn-outline-light btn-lg"><i class="fas fa-phone me-2"></i>%s</a>\n'
        '                </div>\n'
        '            </div>\n        </header>'
        % (e("Parroquia " + parroquia if es_parroquia else "Capital: " + m["capital"]), e(m["nombre"]), e(ESTADO),
           e(h1), e(intro[0]), e(intro[1]), e(intro[2]),
           e(wa("Hola, necesito un abogado en %s, Municipio %s" % (lugar, m["nombre"]))), tel(), e(SITIO["telefono_local"])),
        html_saren_bloque(lugar),
        html_servicios(lugar, m["nombre"], semilla),
        html_pasos(PASOS_LANDING, "Cómo funciona"),
        html_faq(faqs, "Preguntas frecuentes en %s" % lugar),
        html_enlaces(m, parroquia),
        html_cta_final(lugar),
    ])
    lugar_geo = "%s, Municipio %s, %s, %s" % (lugar, m["nombre"], ESTADO, SITIO["pais"])
    escribir(os.path.join(RAIZ, ruta.strip("/"), "index.html"),
             pagina(titulo, desc, ruta, cuerpo, grafo, "Hola, vengo de la página web y necesito un abogado en %s, Municipio %s" % (lugar, m["nombre"]), lugar=lugar_geo))
    return ruta


def indice_abogados():
    ruta = "/abogados/"
    titulo = "Abogados en %s: todos los municipios y parroquias" % ESTADO
    desc = "Abogados en los %d municipios y %d parroquias del estado %s: %s, registros, notarías, contratos, divorcios y herencias." % (
        len(MUNICIPIOS), sum(len(m["parroquias"]) for m in MUNICIPIOS), ESTADO, DESTACADO)
    migas = [("Inicio", "/"), ("Abogados en %s" % ESTADO, ruta)]
    grupos = []
    for m in MUNICIPIOS:
        filas = ['                        <a class="ios-row" href="%s"><span><strong>Municipio %s</strong><small>Capital: %s</small></span></a>' % (url_mun(m), e(m["nombre"]), e(m["capital"]))]
        filas += ['                        <a class="ios-row" href="%s"><span>Parroquia %s</span></a>' % (url_par(m, p), e(p)) for p in m["parroquias"]]
        grupos.append('                <div class="col-md-6 col-lg-4">\n                    <p class="ios-group-title">%s</p>\n'
                      '                    <div class="ios-group">\n%s\n                    </div>\n                </div>' % (e(m["nombre"]), "\n".join(filas)))
    cuerpo = "\n\n".join([
        html_migas(migas),
        '        <header class="lp-hero">\n            <div class="container">\n'
        '                <h1>Abogados en el estado %s</h1>\n'
        '                <p class="lp-lead">Elige tu municipio o parroquia para ver los servicios legales disponibles en tu zona, con atención por WhatsApp y teléfono.</p>\n'
        '            </div>\n        </header>' % e(ESTADO),
        '        <section class="lp-seccion">\n            <div class="container">\n                <div class="row g-3">\n%s\n                </div>\n'
        '            </div>\n        </section>' % "\n".join(grupos),
        html_cta_final(ESTADO),
    ])
    grafo = [
        {"@type": "CollectionPage", "@id": DOM + ruta + "#webpage", "url": DOM + ruta, "name": titulo,
         "description": desc, "inLanguage": "es-VE", "isPartOf": {"@id": WEB_ID}},
        organizacion(),
        servicio_legal(lugar_estado()),
        migas_ld(migas),
    ]
    escribir(os.path.join(RAIZ, "abogados", "index.html"),
             pagina(titulo, desc, ruta, cuerpo, grafo, "Hola, vengo de la página web y necesito un abogado en %s" % ESTADO))
    return ruta


def landing_saren():
    ruta = "/saren-en-linea/"
    titulo = "SAREN en línea: trámites, recaudos y paso a paso | %s" % SITIO["nombre"]
    desc = ("Gestión de trámites SAREN en línea: legalizaciones, autenticaciones, poderes, compraventas y registro de empresas. "
            "Recaudos, paso a paso y preguntas frecuentes. Gestores independientes.")
    migas = [("Inicio", "/"), (DESTACADO, ruta)]
    tramites = "\n".join(
        '                    <div class="col-md-6 col-lg-3">\n'
        '                        <div class="lp-servicio">\n'
        '                            <h3>%s</h3>\n                            <p>%s</p>\n'
        '                            <a href="%s" class="btn btn-success btn-sm" target="_blank" rel="noopener"><i class="fab fa-whatsapp me-1"></i>Solicitar</a>\n'
        '                        </div>\n                    </div>' % (e(t), e(d), e(wa("Hola, necesito ayuda con: %s (SAREN en línea)" % t)))
        for t, d in SAREN_TRAMITES)
    recaudos = "\n".join('                        <li class="ios-row"><i class="fas fa-file-alt text-primary"></i> %s</li>' % e(r) for r in SAREN_RECAUDOS)
    cuerpo = "\n\n".join([
        html_migas(migas),
        '        <header class="lp-hero">\n            <div class="container">\n'
        '                <span class="lp-etiqueta"><i class="fas fa-star me-1"></i> Servicio destacado</span>\n'
        '                <h1>SAREN en línea: gestionamos tu trámite de principio a fin</h1>\n'
        '                <p class="lp-lead">Te ayudamos con legalizaciones, autenticaciones, poderes, compraventas, registro de empresas y citas ante registros y notarías, en %s y en toda Venezuela.</p>\n'
        '                <div class="lp-botones">\n'
        '                    <a href="%s" class="btn btn-success btn-lg" target="_blank" rel="noopener"><i class="fab fa-whatsapp me-2"></i>Consultar por WhatsApp</a>\n'
        '                    <a href="%s" class="btn btn-outline-light btn-lg"><i class="fas fa-phone me-2"></i>%s</a>\n'
        '                </div>\n'
        '            </div>\n        </header>' % (e(ESTADO), e(wa("Hola, vengo de la página web y necesito un trámite de SAREN en línea")), tel(), e(SITIO["telefono_local"])),
        '        <section class="lp-seccion">\n            <div class="container lp-estrecho">\n'
        '                <div class="lp-aviso" role="note"><i class="fas fa-info-circle me-2"></i><strong>Aclaración importante:</strong> somos abogados y gestores independientes. '
        'No somos el SAREN (Servicio Autónomo de Registros y Notarías) ni una oficina oficial del Estado. '
        'Los aranceles y tasas oficiales se pagan aparte de nuestros honorarios. El portal oficial es '
        '<a href="https://www.saren.gob.ve/" target="_blank" rel="noopener">saren.gob.ve</a>.</div>\n'
        '            </div>\n        </section>',
        '        <section class="lp-seccion lp-gris">\n            <div class="container">\n'
        '                <h2 class="lp-h2">Trámites que gestionamos</h2>\n                <div class="row g-3">\n%s\n                </div>\n'
        '            </div>\n        </section>' % tramites,
        '        <section class="lp-seccion">\n            <div class="container lp-estrecho">\n'
        '                <h2 class="lp-h2">Recaudos habituales</h2>\n'
        '                <p class="text-center">Los recaudos exactos dependen del trámite; te confirmamos la lista al revisar tu caso.</p>\n'
        '                <ul class="ios-group">\n%s\n                </ul>\n'
        '            </div>\n        </section>' % recaudos,
        html_pasos(SAREN_PASOS, "Paso a paso"),
        html_faq(SAREN_FAQ, "Preguntas frecuentes sobre SAREN en línea"),
        '        <section class="lp-seccion">\n            <div class="container">\n'
        '                <h2 class="lp-h2">Más información</h2>\n'
        '                <div class="ios-group lp-estrecho mx-auto">\n'
        '                    <a class="ios-row" href="/servicios/tramites-saren/"><span>Trámites SAREN</span></a>\n'
        '                    <a class="ios-row" href="/tramites-en-linea/saren/"><span>Trámites SAREN en línea: apostillas, legalizaciones y citas</span></a>\n'
        '                    <a class="ios-row" href="/servicios/registros-notarias/"><span>Registros y notarías</span></a>\n'
        '                    <a class="ios-row" href="/abogados/"><span>Abogados en los municipios de %s</span></a>\n'
        '                </div>\n'
        '            </div>\n        </section>' % e(ESTADO),
        html_cta_final(ESTADO),
    ])
    grafo = [
        {"@type": "WebPage", "@id": DOM + ruta + "#webpage", "url": DOM + ruta, "name": titulo,
         "description": desc, "inLanguage": "es-VE", "isPartOf": {"@id": WEB_ID}},
        organizacion(),
        servicio_legal(lugar_estado()),
        {"@type": "Service", "name": DESTACADO, "serviceType": "Gestión de trámites ante registros y notarías",
         "provider": {"@id": LEGAL_ID}, "areaServed": [lugar_estado(), {"@type": "Country", "name": SITIO["pais"]}],
         "url": DOM + ruta,
         "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Trámites SAREN en línea",
                             "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": t, "description": d}} for t, d in SAREN_TRAMITES]}},
        migas_ld(migas),
        faq_ld(SAREN_FAQ),
        howto_ld("Cómo hacer un trámite de SAREN en línea con nosotros", SAREN_PASOS),
    ]
    escribir(os.path.join(RAIZ, "saren-en-linea", "index.html"),
             pagina(titulo, desc, ruta, cuerpo, grafo, "Hola, vengo de la página web (SAREN en línea) y necesito un trámite"))
    return ruta


def pagina_404():
    titulo = "Página no encontrada | %s" % SITIO["nombre"]
    desc = "La página que buscas no existe o cambió de dirección."
    cuerpo = ('        <header class="lp-hero lp-404">\n            <div class="container text-center">\n'
              '                <h1>Página no encontrada</h1>\n'
              '                <p class="lp-lead">La dirección que buscas no existe o cambió. Puedes volver al inicio o escribirnos directamente.</p>\n'
              '                <div class="lp-botones justify-content-center">\n'
              '                    <a href="/" class="btn btn-primary btn-lg"><i class="fas fa-home me-2"></i>Ir al inicio</a>\n'
              '                    <a href="/abogados/" class="btn btn-outline-light btn-lg">Municipios</a>\n'
              '                    <a href="/saren-en-linea/" class="btn btn-outline-light btn-lg">SAREN en línea</a>\n'
              '                </div>\n'
              '            </div>\n        </header>')
    doc = pagina(titulo, desc, "/404.html", cuerpo, [organizacion(), sitio_web()],
                 "Hola, vengo de la página web y necesito asesoría legal")
    doc = doc.replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex, follow">')
    doc = re.sub(r'    <link rel="canonical" href="[^"]+">\n', "", doc)
    escribir(os.path.join(RAIZ, "404.html"), doc)


# ---------------------------------------------------------------------------
# 3) Archivos del sitio
# ---------------------------------------------------------------------------
def todas_las_urls():
    urls = []
    for base, dirs, archivos in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "tools", "assets")]
        if "index.html" in archivos:
            rel = os.path.relpath(base, RAIZ).replace(os.sep, "/")
            urls.append("/" if rel == "." else "/%s/" % rel)
    return urls


def sitemap():
    def prioridad(u):
        if u == "/":
            return "1.00", "daily"
        if u in ("/saren-en-linea/", "/abogados/"):
            return "0.95", "weekly"
        if u.startswith("/servicios/"):
            return "0.90", "weekly"
        if u.startswith("/abogados/"):
            return ("0.85" if u.count("/") == 3 else "0.80"), "monthly"
        return "0.80", "monthly"
    urls = sorted(todas_las_urls(), key=lambda u: (u != "/", not u.startswith("/saren"), u))
    filas = []
    for u in urls:
        p, f = prioridad(u)
        filas.append("    <url>\n        <loc>%s%s</loc>\n        <lastmod>%s</lastmod>\n        <changefreq>%s</changefreq>\n        <priority>%s</priority>\n    </url>"
                     % (DOM, u, HOY, f, p))
    escribir(os.path.join(RAIZ, "sitemap.xml"),
             '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % "\n".join(filas))
    return urls


def manifest():
    datos = {
        "name": "%s - Abogados en %s" % (SITIO["nombre"], ESTADO),
        "short_name": SITIO["nombre"],
        "description": SITIO["descripcion_corta"],
        "lang": "es-VE",
        "start_url": "/?utm_source=pwa",
        "scope": "/",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": SITIO["theme_color"],
        "icons": [
            {"src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "/assets/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
            {"src": "/assets/icons/favicon.svg", "sizes": "any", "type": "image/svg+xml"},
        ],
    }
    escribir(os.path.join(RAIZ, "manifest.webmanifest"), json.dumps(datos, ensure_ascii=False, indent=2) + "\n")


def headers():
    escribir(os.path.join(RAIZ, "_headers"), """# Cabeceras para Cloudflare Pages
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=()

/assets/*
  Cache-Control: public, max-age=604800

/images/*
  Cache-Control: public, max-age=604800

/manifest.webmanifest
  Content-Type: application/manifest+json
  Cache-Control: public, max-age=86400

/sitemap.xml
  Content-Type: application/xml; charset=utf-8
""")


def enlaces_internos_sin_pagina():
    """Rutas internas enlazadas desde el HTML que no tienen archivo."""
    faltan = set()
    for base, dirs, archivos in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "tools")]
        for a in archivos:
            if not a.endswith(".html"):
                continue
            ruta_doc = os.path.join(base, a)
            for href in re.findall(r'href="([^"]+)"', leer(ruta_doc)):
                if href.startswith(("http", "mailto:", "tel:", "#", "javascript:")):
                    continue
                camino = href.split("#")[0].split("?")[0]
                if not camino:
                    continue
                if camino.startswith("/"):
                    destino = os.path.join(RAIZ, camino.lstrip("/"))
                else:
                    destino = os.path.normpath(os.path.join(base, camino))
                if os.path.isdir(destino):
                    destino = os.path.join(destino, "index.html")
                if not os.path.exists(destino) and camino.startswith("/") and camino.endswith("/"):
                    faltan.add(camino)
    return sorted(faltan)


def redirects():
    """Al existir 404.html, Cloudflare Pages deja de servir la portada para
    rutas desconocidas. Para no romper los enlaces del menú que ya existían
    y hoy muestran la portada, se redirigen temporalmente (302) a la portada."""
    faltan = enlaces_internos_sin_pagina()
    lineas = ["# Generado por tools/generar_landings.py",
              "# Enlaces del menú existente que aún no tienen página: se envían a la portada",
              "# (comportamiento equivalente al que tenían antes de añadir 404.html)."]
    lineas += ["%s / 302" % f for f in faltan]
    escribir(os.path.join(RAIZ, "_redirects"), "\n".join(lineas) + "\n")
    return faltan


def main():
    global MENU, PIE, SNIPPET_WA
    aplicar_capa_global()
    MENU, PIE, SNIPPET_WA = extraer_menu_y_pie()
    creadas = [indice_abogados(), landing_saren()]
    for m in MUNICIPIOS:
        creadas.append(landing(m))
        for p in m["parroquias"]:
            creadas.append(landing(m, p))
    pagina_404()
    manifest()
    headers()
    urls = sitemap()
    faltan = redirects()
    print("Páginas generadas: %d" % len(creadas))
    print("URLs en sitemap: %d" % len(urls))
    print("Redirecciones temporales (enlaces existentes sin página): %d" % len(faltan))


if __name__ == "__main__":
    main()
