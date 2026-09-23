#!/usr/bin/env python3
"""
Constructor / validador del sitio estático Abogados Valencia.

Uso:
    python3 tools/build_site.py            # aplica cambios y valida
    python3 tools/build_site.py --check    # solo valida (no escribe)

Qué hace (idempotente, se puede ejecutar varias veces):
  1. Genera las landing de estados que faltan o que eran copias de otro estado
     (usa estados/apure/ como plantilla).
  2. Genera páginas institucionales: Quiénes Somos, Política de Privacidad,
     Tratamiento de Datos, índice de Estados, índice de Trámites en Línea y
     Solicitudes Legales.
  3. En TODAS las páginas:
       - menú unificado (sin enlaces rotos) con "Trámites SAREN en Línea",
       - H1/título "Abogados en <Estado>" en las landing de estado,
       - identificador "g33" al final de cada mensaje de WhatsApp,
       - bloque de servicio "Trámites SAREN en Línea",
       - enlaces legales en el pie, año de copyright y horario unificados,
       - Google Analytics y schema.org (JSON-LD) con los datos del perfil.
  4. Regenera sitemap.xml y valida enlaces internos, H1, canonical y schema.

Los datos del negocio (NAP) están SOLO en NEGOCIO: si cambian en el perfil de
Google Business, se editan aquí y se vuelve a ejecutar el script.
"""
import html
import json
import os
import re
import shutil
import sys
from datetime import date
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://abogadosvalencia.pages.dev"
TODAY = date.today().isoformat()
YEAR = date.today().year
GA_ID = "G-RFW5F7YBBR"

# --------------------------------------------------------------------------
# Datos del negocio: deben coincidir con el perfil de Google Business
# https://maps.app.goo.gl/SuvKMZ2aup2iWXyV6
# --------------------------------------------------------------------------
NEGOCIO = {
    "nombre": "Abogados Valencia",
    "nombre_google": "Abogados Valencia ⚖️ | 🟢 Trámites de Notaría y Registro en Barinas - Civil y Familia",
    # Descripción, categorías, fecha de apertura, horario y ubicación tomados
    # del perfil de Google Business.
    "descripcion": "Abogados Valencia es su aliado experto en trámites de notaría y registro en Barinas. "
                   "Nos especializamos en Derecho Civil y Familia, ofreciendo soluciones ágiles en procesos "
                   "de divorcio y protección ante el Tribunal Tercero de Menores de Barinas. Gestionamos la "
                   "redacción de documentos, poderes, ventas de vehículos y gestiones ante el Registro Civil, "
                   "mercantil e inmobiliario, y brindamos asesoría en actas, sucesiones y herencias.",
    "descripcion_corta": "Bufete de abogados en Barinas, Venezuela: trámites de notaría y registro, derecho civil "
                         "y familia, y trámites SAREN en línea en todo el país.",
    "categorias": ["Abogado", "Servicios legales", "Abogado civil", "Abogado de derecho de familia",
                   "Abogado general"],
    "fecha_apertura": "2010-03-16",
    "fecha_apertura_texto": "16 de marzo de 2010",
    "anio_apertura": 2010,
    "telefono": "+584245112587",
    "telefono_visible": "+58 424-5112587",
    "telefono2": "+584126015769",
    "telefono2_visible": "+58 412-6015769",
    "facebook": "https://www.facebook.com/Abogadosenbarinas",
    # Áreas de servicio del perfil de Google
    "areas_servicio": [
        ("Barinas", "5201", "Barinas"), ("Barinitas", "5206", "Barinas"), ("Barrancas", "5211", "Barinas"),
        ("La Luz", "5212", "Barinas"), ("Pedraza", "5214", "Barinas"), ("Socopó", "5216", "Barinas"),
        ("Sabaneta", "5224", "Barinas"), ("Valencia", "", "Carabobo"), ("Ciudad Guayana", "", "Bolívar"),
        ("San Cristóbal", "", "Táchira"), ("Caracas", "", "Distrito Capital"),
        ("", "", "Lara"), ("", "", "Miranda"), ("", "", "Guárico"),
    ],
    "whatsapp": "584245112587",
    "google_maps": "https://maps.app.goo.gl/SuvKMZ2aup2iWXyV6",
    # Calificación pública en Google (se muestra en la web, no en el schema:
    # Google no admite reseñas propias del negocio como rich result).
    "google_calificacion": "5.0",
    "google_opiniones": 10,
    "google_resena": {"autor": "Marco F. (Local Guide)", "texto": "Trabajo muy profesional y ordenado",
                      "detalle": "Precio razonable"},
    # Dirección exacta del perfil de Google.
    "direccion": {
        "streetAddress": "Frente al Registro Público Inmobiliario, C.C Sabana Grande Avenida 23 de Enero",
        "addressLocality": "Barinas",
        "addressRegion": "Barinas",
        "postalCode": "5201",
        "addressCountry": "VE",
    },
    # Perfil de Google: "Abierto las 24 horas"
    "horario": [
        {"dias": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
         "abre": "00:00", "cierra": "23:59", "texto": "Abierto las 24 horas, todos los días",
         "corto": "Abierto las 24 horas"},
    ],
    "accesible_silla_ruedas": True,
    "logo": BASE_URL + "/images/logo-abogados-en-venezuela-apure-barinas-valencia-caracas-zulia-lara-servicios-saren-en-linea.jpg",
    "imagen": BASE_URL + "/images/abogados-en-barinas-tramines-legales-abogado-notaria-registro-tribunales.jpg",
}

WA_TAG = "g33"
WA_BASE = "https://wa.me/" + NEGOCIO["whatsapp"]
WA_GENERIC = "estoy%20escribiendo%20desde%20la%20pagina%20web%20estoy%20interesado%20en%20uno%20de%20tus%20servicios"

SERVICIOS = [
    ("Trámites SAREN en Línea", "/tramites-en-linea/saren/"),
    ("Trámites SAREN", "/servicios/tramites-saren/"),
    ("Derecho Civil", "/servicios/derecho-civil/"),
    ("Registros y Notarías", "/servicios/registros-notarias/"),
    ("Documentos Legales", "/servicios/documentos-legales/"),
    ("Contratos", "/servicios/contratos/"),
    ("Registro Civil en Línea", "/tramites-en-linea/registro-civil/"),
    ("Trámites Notariales en Línea", "/tramites-en-linea/notarias/"),
    ("Solicitudes Legales (visas y pasaportes)", "/tramites-en-linea/solicitudes/"),
]

# --------------------------------------------------------------------------
# Estados de Venezuela
#   nombre, capital, cantidad de municipios (o parroquias), unidad,
#   municipios/parroquias destacados [(nombre, detalle)]
# --------------------------------------------------------------------------
ESTADOS = {
    "amazonas": ("Amazonas", "Puerto Ayacucho", 7, "municipios", None),
    "anzoategui": ("Anzoátegui", "Barcelona", 21, "municipios", None),
    "apure": ("Apure", "San Fernando de Apure", 7, "municipios", None),
    "aragua": ("Aragua", "Maracay", 18, "municipios", None),
    "barinas": ("Barinas", "Barinas", 12, "municipios", None),
    "bolivar": ("Bolívar", "Ciudad Bolívar", 11, "municipios", None),
    "carabobo": ("Carabobo", "Valencia", 14, "municipios", None),
    "cojedes": ("Cojedes", "San Carlos", 9, "municipios", None),
    "delta-amacuro": ("Delta Amacuro", "Tucupita", 4, "municipios", [
        ("Tucupita", "Capital del estado"), ("Antonio Díaz", "Curiapo"),
        ("Casacoima", "Sierra Imataca"), ("Pedernales", "Pedernales")]),
    "falcon": ("Falcón", "Coro", 25, "municipios", [
        ("Miranda", "Coro, capital del estado"), ("Carirubana", "Punto Fijo"),
        ("Los Taques", "Santa Cruz de Los Taques"), ("Falcón", "Pueblo Nuevo"),
        ("Zamora", "Puerto Cumarebo"), ("Silva", "Tucacas"), ("Federación", "Churuguara")]),
    "guarico": ("Guárico", "San Juan de los Morros", 15, "municipios", [
        ("Juan Germán Roscio", "San Juan de los Morros, capital"), ("Francisco de Miranda", "Calabozo"),
        ("Leonardo Infante", "Valle de la Pascua"), ("Pedro Zaraza", "Zaraza"),
        ("Julián Mellado", "El Sombrero"), ("José Tadeo Monagas", "Altagracia de Orituco"),
        ("José Félix Ribas", "Tucupido")]),
    "lara": ("Lara", "Barquisimeto", 9, "municipios", [
        ("Iribarren", "Barquisimeto, capital"), ("Palavecino", "Cabudare"), ("Torres", "Carora"),
        ("Jiménez", "Quíbor"), ("Morán", "El Tocuyo"), ("Crespo", "Duaca"), ("Urdaneta", "Siquisique")]),
    "merida": ("Mérida", "Mérida", 23, "municipios", [
        ("Libertador", "Mérida, capital"), ("Alberto Adriani", "El Vigía"), ("Campo Elías", "Ejido"),
        ("Tovar", "Tovar"), ("Sucre", "Lagunillas"), ("Rangel", "Mucuchíes"), ("Santos Marquina", "Tabay")]),
    "miranda": ("Miranda", "Los Teques", 21, "municipios", [
        ("Guaicaipuro", "Los Teques, capital"), ("Sucre", "Petare"), ("Baruta", "Baruta"),
        ("Chacao", "Chacao"), ("Plaza", "Guarenas"), ("Zamora", "Guatire"), ("Cristóbal Rojas", "Charallave")]),
    "monagas": ("Monagas", "Maturín", 13, "municipios", [
        ("Maturín", "Capital del estado"), ("Ezequiel Zamora", "Punta de Mata"), ("Piar", "Aragua de Maturín"),
        ("Caripe", "Caripe"), ("Punceres", "Quiriquire"), ("Sotillo", "Barrancas del Orinoco"),
        ("Cedeño", "Caicara de Maturín")]),
    "nueva-esparta": ("Nueva Esparta", "La Asunción", 11, "municipios", [
        ("Arismendi", "La Asunción, capital"), ("Mariño", "Porlamar"), ("Maneiro", "Pampatar"),
        ("García", "El Valle del Espíritu Santo"), ("Díaz", "San Juan Bautista"),
        ("Antolín del Campo", "La Plaza de Paraguachí"), ("Península de Macanao", "Boca de Río")]),
    "portuguesa": ("Portuguesa", "Guanare", 14, "municipios", [
        ("Guanare", "Capital del estado"), ("Páez", "Acarigua"), ("Araure", "Araure"), ("Ospino", "Ospino"),
        ("Turén", "Villa Bruzual"), ("Guanarito", "Guanarito"), ("Esteller", "Píritu")]),
    "sucre": ("Sucre", "Cumaná", 15, "municipios", [
        ("Sucre", "Cumaná, capital"), ("Bermúdez", "Carúpano"), ("Arismendi", "Río Caribe"),
        ("Ribero", "Cariaco"), ("Benítez", "El Pilar"), ("Valdez", "Güiria"), ("Montes", "Cumanacoa")]),
    "tachira": ("Táchira", "San Cristóbal", 29, "municipios", [
        ("San Cristóbal", "Capital del estado"), ("Cárdenas", "Táriba"), ("Torbes", "San Josecito"),
        ("Bolívar", "San Antonio del Táchira"), ("Pedro María Ureña", "Ureña"),
        ("García de Hevia", "La Fría"), ("Junín", "Rubio")]),
    "trujillo": ("Trujillo", "Trujillo", 20, "municipios", [
        ("Trujillo", "Capital del estado"), ("Valera", "Valera"), ("Boconó", "Boconó"), ("Pampán", "Pampán"),
        ("Rafael Rangel", "Betijoque"), ("Carache", "Carache"), ("Escuque", "Escuque")]),
    "vargas": ("La Guaira (Vargas)", "La Guaira", 11, "parroquias", [
        ("La Guaira", "Capital del estado"), ("Maiquetía", "Aeropuerto internacional"),
        ("Catia La Mar", "Parroquia más poblada"), ("Macuto", "Litoral central"),
        ("Caraballeda", "Litoral central"), ("Naiguatá", "Litoral este"), ("Carayaca", "Litoral oeste")]),
    "yaracuy": ("Yaracuy", "San Felipe", 14, "municipios", [
        ("San Felipe", "Capital del estado"), ("Independencia", "Independencia"), ("Peña", "Yaritagua"),
        ("Nirgua", "Nirgua"), ("Bruzual", "Chivacoa"), ("Sucre", "Guama"), ("Cocorote", "Cocorote")]),
    "zulia": ("Zulia", "Maracaibo", 21, "municipios", [
        ("Maracaibo", "Capital del estado"), ("San Francisco", "San Francisco"), ("Cabimas", "Cabimas"),
        ("Lagunillas", "Ciudad Ojeda"), ("Mara", "San Rafael del Moján"),
        ("Machiques de Perijá", "Machiques"), ("Santa Rita", "Santa Rita")]),
    "distrito-capital": ("Distrito Capital", "Caracas", 22, "parroquias", [
        ("Catedral", "Centro de Caracas"), ("El Recreo", "Sabana Grande"), ("Sucre", "Catia"),
        ("El Paraíso", "El Paraíso"), ("San Juan", "San Juan"), ("La Candelaria", "La Candelaria"),
        ("Antímano", "Antímano")]),
}
# Páginas que se (re)generan desde la plantilla: las que no existían y las que
# eran copias de Cojedes (título/H1/contenido de Cojedes con otra URL).
GENERAR_DESDE_PLANTILLA = [s for s, v in ESTADOS.items() if v[4] is not None]
PLANTILLA_ESTADO = "apure"


def ruta(*p):
    return os.path.join(ROOT, *p)


def leer(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def escribir(p, contenido):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(contenido)


def wa_link(texto):
    return WA_BASE + "?text=" + quote(texto, safe=",") + "%20" + WA_TAG


def unir_y(items):
    return ", ".join(items[:-1]) + " y " + items[-1] if len(items) > 1 else items[0]


# ==========================================================================
# 1. Landing de estados desde la plantilla
# ==========================================================================
def generar_estado(slug):
    nombre, capital, n, unidad, municipios = ESTADOS[slug]
    tpl = leer(ruta("estados", PLANTILLA_ESTADO, "index.html"))
    ini_nav = tpl.index("<!-- ========== MENÚ COMPLETO")
    fin_nav = tpl.index("<!-- ========== FIN MENÚ ========== -->")
    head, nav, cuerpo = tpl[:ini_nav], tpl[ini_nav:fin_nav], tpl[fin_nav:]

    nombres = [m[0] for m in municipios]
    art = "las" if unidad == "parroquias" else "los"
    unidad_cap = unidad.capitalize()

    # Sección de cobertura, específica del estado
    ini = cuerpo.index("<!-- Apure Coverage Section -->")
    fin = cuerpo.index("</section>", ini) + len("</section>")
    items_mun = "\n".join(
        f"                            <li><strong>{m}</strong> - {d}</li>" for m, d in municipios)
    items_srv = "\n".join(
        f'                            <li><a href="#contacto">{s} {m}</a></li>' for s, m in zip(
            ["Trámites SAREN en línea", "Registro Civil", "Notarías", "Visas y pasaportes",
             "Apostillas", "Abogados en"], nombres))
    cobertura = f"""<!-- {nombre} Coverage Section -->
    <section class="categories-section bg-dark" id="cobertura-{slug}">
        <div class="container">
            <h2 class="section-title" data-aos="fade-up">Abogados en Todo el Estado {nombre}</h2>
            <p class="text-center mb-5" data-aos="fade-up">Servicio profesional en {art} {n} {unidad} de {nombre}, con atención presencial coordinada y trámites SAREN en línea</p>

            <div class="row" data-aos="fade-up">
                <div class="col-md-6">
                    <div class="document-category">
                        <h3 class="h4 text-primary mb-3"><i class="fas fa-map-marker-alt me-2"></i> {unidad_cap} de {nombre}</h3>
                        <ul class="service-features">
{items_mun}
                        </ul>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="document-category">
                        <h3 class="h4 text-primary mb-3"><i class="fas fa-globe me-2"></i> Servicios Disponibles</h3>
                        <ul class="service-features">
{items_srv}
                        </ul>
                    </div>
                </div>
            </div>

            <div class="text-center mt-5" data-aos="fade-up" data-aos-delay="200">
                <a href="https://wa.me/584245112587?text=Hola,%20necesito%20servicios%20legales%20en%20mi%20municipio%20de%20{quote(nombre)}" class="btn btn-primary btn-lg">
                    <i class="fab fa-whatsapp me-2"></i> Servicio en Mi Municipio
                </a>
            </div>
        </div>
    </section>"""
    cuerpo = cuerpo[:ini] + cobertura + cuerpo[fin:]

    ap = ["San Fernando", "Biruaca", "Pedro Camejo", "Rómulo Gallegos", "San Camilo", "Páez", "Achaguas"]
    cuerpo = cuerpo.replace("San Fernando de Apure, " + ", ".join(ap[1:-1]) + " y Achaguas", unir_y(nombres))
    cuerpo = cuerpo.replace(", ".join(ap[:-1]) + " y Achaguas", unir_y(nombres))
    cuerpo = cuerpo.replace(", ".join(ap), ", ".join(nombres))
    cuerpo = cuerpo.replace("los 7 municipios", f"{art} {n} {unidad}").replace("los 7 Municipios", f"{art} {n} {unidad.capitalize()}")
    cuerpo = cuerpo.replace("7 municipios", f"{n} {unidad}").replace("7 Municipios", f"{n} {unidad_cap}")
    cuerpo = cuerpo.replace("San Fernando de Apure", capital)
    cuerpo = cuerpo.replace("Apure", nombre)
    # Enlaces de WhatsApp: el nombre del estado debe ir codificado en la URL
    cuerpo = re.sub(r'(href="https://wa\.me/[^"]*)',
                    lambda m: m.group(1).replace(nombre, quote(nombre)), cuerpo)

    head = re.sub(r'<link rel="canonical" href="[^"]*">',
                  f'<link rel="canonical" href="{BASE_URL}/estados/{slug}/">', head)
    desc = (f"Abogados en {nombre}, Venezuela: trámites SAREN en línea, Registro Civil, Notarías, "
            f"apostillas, poderes, visas y pasaportes en {capital} y {art} {n} {unidad} del estado.")
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="{html.escape(desc)}">', head)
    b = nombre.lower()
    kw = (f"abogados en {b}, abogado {b}, abogados {capital.lower()}, trámites saren en línea {b}, saren {b}, "
          f"registro civil {b}, notarías {b}, apostilla {b}, poder notarial {b}, partida de nacimiento {b}, "
          f"acta de nacimiento {b}, antecedentes penales {b}, visa americana {b}, pasaporte venezolano {b}, "
          + ", ".join(x.lower() for x in nombres) +
          ", trámites saren en línea, registro civil en línea, notaría virtual, abogados venezuela, bufete de abogados")
    head = re.sub(r'<meta name="keywords" content="[^"]*">',
                  f'<meta name="keywords" content="{html.escape(kw)}">', head)
    head = head.replace("Apure", nombre)

    destino = ruta("estados", slug)
    os.makedirs(destino, exist_ok=True)
    for f in ("styles.css", "script.js"):
        shutil.copyfile(ruta("estados", PLANTILLA_ESTADO, f), os.path.join(destino, f))
    if os.path.isdir(ruta("estados", PLANTILLA_ESTADO, "images")):
        shutil.copytree(ruta("estados", PLANTILLA_ESTADO, "images"), os.path.join(destino, "images"),
                        dirs_exist_ok=True)
    escribir(os.path.join(destino, "index.html"), head + nav + cuerpo)


# ==========================================================================
# 2. Páginas institucionales / índices
# ==========================================================================
def shell(ruta_url, titulo, descripcion, badge, h1, subtitulo, contenido):
    """Página con la misma estructura visual que el resto del sitio.
    El menú, schema, pie legal y WhatsApp los completa post_procesar()."""
    horario_p = "".join("<p>" + h["texto"] + "</p>" for h in NEGOCIO["horario"])
    return f"""<!DOCTYPE html>
<html lang="es-VE">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Canonical URL -->
    <link rel="canonical" href="{BASE_URL}{ruta_url}">
    <meta name="description" content="{html.escape(descripcion)}">
    <title>{html.escape(titulo)}</title>

    <link rel="shortcut icon" href="/images/abogados-en-barinas-tramines-legales-abogado-notaria-registro-tribunales.jpg" type="image/jpeg">
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- AOS Animation -->
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <!-- Nuestros estilos -->
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- ========== MENÚ COMPLETO ========== -->
    <!-- ========== FIN MENÚ ========== -->

    <!-- Hero Section -->
    <section class="hero-section" id="inicio">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-9" data-aos="fade-right">
                    <span class="hero-badge">{badge}</span>
                    <h1 class="hero-title">{h1}</h1>
                    <p class="hero-subtitle">{subtitulo}</p>
                </div>
            </div>
        </div>
    </section>

{contenido}

    <!-- Contact Section -->
    <section class="contact-section" id="contacto">
        <div class="container">
            <h2 class="section-title" data-aos="fade-up">Contáctenos</h2>
            <div class="contact-info">
                <div class="contact-item">
                    <div class="contact-icon"><i class="fas fa-phone"></i></div>
                    <div>
                        <h5>WhatsApp y Teléfono</h5>
                        <p>+58 424-5112587</p>
                    </div>
                </div>
                <div class="contact-item">
                    <div class="contact-icon"><i class="fas fa-map-marker-alt"></i></div>
                    <div>
                        <h5>Ubicación</h5>
                        <p>Cobertura en todos los estados de Venezuela</p>
                    </div>
                </div>
                <div class="contact-item">
                    <div class="contact-icon"><i class="fas fa-clock"></i></div>
                    <div>
                        <h5>Horario</h5>
                        {horario_p}
                    </div>
                </div>
            </div>
            <div class="mt-4">
                <a href="https://wa.me/584245112587?text={WA_GENERIC}" class="btn btn-primary btn-lg me-2">
                    <i class="fab fa-whatsapp me-2"></i> Consulta por WhatsApp
                </a>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="row">
                <div class="col-lg-6 mb-4 mb-lg-0">
                    <div class="footer-logo">ABOGADOS <span>VALENCIA</span></div>
                    <p class="mb-3">{NEGOCIO['descripcion_corta']}</p>
                </div>
                <div class="col-lg-6">
                    <div class="footer-links">
                        <h5>Contacto</h5>
                        <ul>
                            <li><i class="fas fa-phone me-2"></i> {NEGOCIO['telefono_visible']}</li>
                            <li><i class="fas fa-map-marker-alt me-2"></i> Cobertura Nacional</li>
                            <li><i class="fas fa-clock me-2"></i> {NEGOCIO['horario'][0]['corto']}</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="footer-bottom">
                <p class="mb-0">&copy; {YEAR} Abogados Valencia - Bufete de abogados en Venezuela.</p>
            </div>
        </div>
    </footer>

    <!-- WhatsApp Float -->
    <a href="https://wa.me/584245112587?text={WA_GENERIC}" class="whatsapp-float" target="_blank">
        <i class="fab fa-whatsapp"></i>
    </a>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script src="script.js"></script>
</body>
</html>
"""


def seccion(titulo, html_interno, fondo=""):
    return f"""    <section class="py-5 pagina-institucional {fondo}">
        <div class="container">
            <h2 class="section-title" data-aos="fade-up">{titulo}</h2>
            <div data-aos="fade-up">
{html_interno}
            </div>
        </div>
    </section>"""


def generar_paginas_institucionales():
    horario = "; ".join(h["texto"] for h in NEGOCIO["horario"])
    tel = NEGOCIO["telefono_visible"]
    paginas = {}

    paginas["/quienes-somos/"] = shell(
        "/quienes-somos/", "Quiénes Somos | Abogados Valencia – Bufete de Abogados en Venezuela",
        "Conozca a Abogados Valencia: bufete de abogados en Barinas desde 2010, especializado en derecho civil, "
        "familia, trámites de notaría y registro y trámites SAREN en línea en toda Venezuela.",
        "Nuestro Bufete", 'Quiénes Somos: <span class="text-accent">Abogados Valencia</span>',
        "Bufete de abogados con sede en Barinas desde 2010, dedicado a la asesoría legal y a la gestión de trámites SAREN en línea, "
        "registros, notarías y documentos legales en todo el país y para venezolanos en el exterior.",
        seccion("Nuestra Historia", f"""                <p><strong>Abogados Valencia</strong> abrió sus puertas el <strong>{NEGOCIO['fecha_apertura_texto']}</strong> en <strong>Barinas</strong>. Desde entonces somos aliados de nuestros clientes en trámites de notaría y registro, derecho civil y derecho de familia en la región llanera y, hoy, en toda Venezuela gracias a los trámites SAREN en línea.</p>
                <p>{NEGOCIO['descripcion']}</p>""")
        + "\n" + seccion("Nuestra Misión", """                <p>En <strong>Abogados Valencia</strong> acompañamos a personas, familias y empresas en sus asuntos legales con un servicio cercano, claro y con seguimiento de principio a fin. Combinamos la atención presencial con la gestión de <strong>trámites SAREN en línea</strong> para que nuestros clientes resuelvan sus documentos sin importar en qué estado de Venezuela o en qué país se encuentren.</p>
                <p>Nuestro equipo de abogados trabaja en derecho civil, derecho de familia, sucesiones, contratos, registros y notarías, además de la gestión de apostillas, legalizaciones, poderes y documentos para el exterior.</p>""")
        + "\n" + seccion("Qué Hacemos", "                <ul class=\"service-features\">\n" + "\n".join(
            f'                    <li><a href="{u}">{n}</a></li>' for n, u in SERVICIOS) + "\n                </ul>", "bg-dark")
        + "\n" + seccion("Nuestros Valores", """                <ul class="service-features">
                    <li><strong>Transparencia:</strong> explicamos requisitos, costos y tiempos antes de iniciar cada trámite.</li>
                    <li><strong>Confidencialidad:</strong> la información de cada cliente se trata bajo secreto profesional.</li>
                    <li><strong>Cobertura nacional:</strong> atendemos los 24 estados de Venezuela y a venezolanos en el exterior.</li>
                    <li><strong>Seguimiento:</strong> informamos el avance de cada caso por WhatsApp.</li>
                </ul>""")
        + "\n" + seccion("Datos del Negocio", f"""                <ul class="service-features">
                    <li><strong>Nombre:</strong> {NEGOCIO['nombre']}</li>
                    <li><strong>Categorías:</strong> {", ".join(NEGOCIO['categorias'])}</li>
                    <li><strong>Dirección:</strong> {direccion_texto()}, Venezuela · Entrada accesible para sillas de ruedas</li>
                    <li><strong>Fecha de apertura:</strong> {NEGOCIO['fecha_apertura_texto']}</li>
                    <li><strong>Calificación en Google:</strong> {NEGOCIO['google_calificacion']} ★ ({NEGOCIO['google_opiniones']} opiniones)</li>
                    <li><strong>Teléfono / WhatsApp:</strong> <a href="tel:{NEGOCIO['telefono']}">{tel}</a> (principal) · <a href="tel:{NEGOCIO['telefono2']}">{NEGOCIO['telefono2_visible']}</a></li>
                    <li><strong>Facebook:</strong> <a href="{NEGOCIO['facebook']}" target="_blank" rel="noopener">facebook.com/Abogadosenbarinas</a></li>
                    <li><strong>Horario:</strong> {horario}</li>
                    <li><strong>Perfil de Google:</strong> <a href="{NEGOCIO['google_maps']}" target="_blank" rel="noopener">Ver en Google Maps</a></li>
                </ul>""", "bg-dark")
        + "\n" + seccion("Áreas de Servicio", "                <ul class=\"service-features\">\n" + "\n".join(
            f"                    <li>{a}, Venezuela</li>" for a in areas_texto()) +
            "\n                </ul>\n                <p>Además atendemos trámites SAREN en línea en <a href=\"/estados-venezuela/\">todos los estados de Venezuela</a>.</p>"))

    ultima = date.today().strftime("%d/%m/%Y")
    paginas["/politica-de-privacidad/"] = shell(
        "/politica-de-privacidad/", "Política de Privacidad | Abogados Valencia",
        "Política de privacidad de Abogados Valencia: qué datos recopilamos, para qué los usamos, "
        "cómo los protegemos y cómo ejercer sus derechos.",
        "Información Legal", 'Política de <span class="text-accent">Privacidad</span>',
        f"Última actualización: {ultima}. Esta política explica cómo Abogados Valencia trata la información de las personas que visitan este sitio web o nos contactan.",
        seccion("1. Responsable", f"""                <p>El responsable del sitio <strong>{BASE_URL}</strong> es <strong>{NEGOCIO['nombre']}</strong>, contacto: <a href="tel:{NEGOCIO['telefono']}">{tel}</a> (teléfono y WhatsApp).</p>""")
        + "\n" + seccion("2. Datos que recopilamos", """                <ul class="service-features">
                    <li><strong>Datos que usted nos envía</strong> por WhatsApp o teléfono: nombre, número de contacto, estado o ciudad y la información del trámite que solicita.</li>
                    <li><strong>Datos de navegación</strong> recopilados por Google Analytics (páginas visitadas, dispositivo, país aproximado) de forma agregada.</li>
                    <li>Los mensajes de WhatsApp enviados desde este sitio incluyen el código <strong>g33</strong> y el nombre de la página, únicamente para identificar que el contacto proviene de la web.</li>
                </ul>""", "bg-dark")
        + "\n" + seccion("3. Finalidad", """                <p>Usamos los datos para responder consultas, preparar presupuestos, gestionar los trámites legales encargados y mejorar el sitio web. No vendemos ni cedemos datos personales a terceros con fines comerciales.</p>""")
        + "\n" + seccion("4. Cookies y servicios de terceros", """                <p>Este sitio utiliza Google Analytics y recursos de terceros (Bootstrap, Font Awesome, AOS) cargados desde CDN. Estos proveedores pueden usar cookies propias. Puede bloquear o eliminar las cookies desde la configuración de su navegador.</p>""", "bg-dark")
        + "\n" + seccion("5. Sus derechos", """                <p>Puede solicitar el acceso, la rectificación o la eliminación de sus datos escribiéndonos por WhatsApp. Consulte también nuestra <a href="/tratamiento-de-datos/">Política de Tratamiento de Datos</a>.</p>"""))

    paginas["/tratamiento-de-datos/"] = shell(
        "/tratamiento-de-datos/", "Tratamiento de Datos Personales | Abogados Valencia",
        "Política de tratamiento de datos personales de Abogados Valencia: base legal, conservación, "
        "seguridad y derechos del titular conforme a la Constitución de Venezuela.",
        "Información Legal", 'Tratamiento de <span class="text-accent">Datos Personales</span>',
        f"Última actualización: {ultima}. Condiciones con las que Abogados Valencia trata los datos personales de clientes y usuarios.",
        seccion("Base legal", """                <p>El tratamiento se realiza con el consentimiento del titular y para la ejecución del servicio solicitado, respetando el derecho a la protección de datos y el <em>habeas data</em> reconocidos en los artículos 28 y 60 de la Constitución de la República Bolivariana de Venezuela, así como el secreto profesional del abogado.</p>""")
        + "\n" + seccion("Datos tratados", """                <ul class="service-features">
                    <li>Identificación: nombre, cédula o pasaporte cuando el trámite lo requiere.</li>
                    <li>Contacto: teléfono, WhatsApp y correo electrónico.</li>
                    <li>Documentos necesarios para el trámite (actas, partidas, poderes, títulos, etc.).</li>
                </ul>""", "bg-dark")
        + "\n" + seccion("Conservación y seguridad", """                <p>Los datos se conservan solo durante el tiempo necesario para prestar el servicio y cumplir obligaciones legales. Aplicamos medidas razonables de seguridad y el acceso está limitado al personal que gestiona el caso.</p>""")
        + "\n" + seccion("Derechos del titular", """                <p>Usted puede conocer, actualizar, rectificar o solicitar la eliminación de sus datos, así como revocar su consentimiento, escribiéndonos por WhatsApp. Responderemos en un plazo máximo de 15 días hábiles. Más información en la <a href="/politica-de-privacidad/">Política de Privacidad</a>.</p>""", "bg-dark"))

    tarjetas = "\n".join(
        f"""                <div class="col-md-4 col-lg-3 mb-3"><a class="btn btn-outline-primary w-100" href="/estados/{s}/">Abogados en {v[0]}</a></div>"""
        for s, v in sorted(ESTADOS.items(), key=lambda kv: kv[1][0]))
    paginas["/estados-venezuela/"] = shell(
        "/estados-venezuela/", "Abogados en los Estados de Venezuela | Trámites SAREN en Línea | Abogados Valencia",
        "Abogados en los 24 estados de Venezuela: trámites SAREN en línea, Registro Civil, notarías, apostillas "
        "y asesoría legal. Elija su estado.",
        "Cobertura Nacional", 'Abogados en los <span class="text-accent">Estados de Venezuela</span>',
        "Seleccione su estado para ver los servicios de abogados, trámites SAREN en línea, Registro Civil y notarías disponibles.",
        seccion("Elija su Estado", f'                <div class="row">\n{tarjetas}\n                </div>'))

    tl = [("Trámites SAREN en Línea", "/tramites-en-linea/saren/", "Apostillas, legalizaciones, citas y documentos ante el SAREN."),
          ("Registro Civil en Línea", "/tramites-en-linea/registro-civil/", "Actas y partidas de nacimiento, matrimonio y defunción."),
          ("Trámites Notariales", "/tramites-en-linea/notarias/", "Poderes, autenticaciones, escrituras y firmas notariales."),
          ("Solicitudes Legales", "/tramites-en-linea/solicitudes/", "Visas, pasaportes, antecedentes penales y trámites migratorios.")]
    tarjetas = "\n".join(f"""                <div class="col-md-6 mb-4"><div class="document-category h-100">
                    <h3 class="h4 text-primary"><a href="{u}">{n}</a></h3><p>{d}</p>
                    <a class="btn btn-sm btn-primary" href="{u}">Ver trámite</a></div></div>""" for n, u, d in tl)
    paginas["/tramites-en-linea/"] = shell(
        "/tramites-en-linea/", "Trámites en Línea en Venezuela – SAREN, Registro Civil y Notarías | Abogados Valencia",
        "Trámites legales en línea en Venezuela: SAREN, Registro Civil, notarías, apostillas, visas y pasaportes. "
        "Gestión completa por abogados.",
        "Trámites Digitales", 'Trámites <span class="text-accent">en Línea</span> en Venezuela',
        "Gestionamos sus trámites SAREN en línea, del Registro Civil y notariales desde cualquier estado de Venezuela o desde el exterior.",
        seccion("Elija su Trámite", f'                <div class="row">\n{tarjetas}\n                </div>'))

    wa = lambda t: f"https://wa.me/584245112587?text={quote(t, safe=',')}"
    items = [("Visa americana", "Formulario DS-160, pago y agendamiento de cita."),
             ("Pasaporte venezolano", "Solicitud y seguimiento ante el SAIME."),
             ("Antecedentes penales", "Certificado de antecedentes penales y su apostilla."),
             ("Apostilla de documentos", "Apostilla electrónica de títulos, actas y antecedentes."),
             ("Poderes para el exterior", "Poderes notariales y consulares con validez internacional."),
             ("Trámites migratorios", "Documentos para residencia, nacionalidad y reagrupación familiar.")]
    tarjetas = "\n".join(f"""                <div class="col-md-6 col-lg-4 mb-4"><div class="document-category h-100">
                    <h3 class="h4 text-primary">{n}</h3><p>{d}</p>
                    <a class="btn btn-sm btn-primary" href="{wa('Hola, quiero solicitar ' + n.lower())}"><i class="fab fa-whatsapp me-1"></i> Solicitar</a></div></div>""" for n, d in items)
    paginas["/tramites-en-linea/solicitudes/"] = shell(
        "/tramites-en-linea/solicitudes/", "Solicitudes Legales en Línea – Visas, Pasaportes y Apostillas | Abogados Valencia",
        "Solicitudes legales en línea en Venezuela: visa americana, pasaporte, antecedentes penales, apostillas "
        "y poderes para el exterior, gestionados por abogados.",
        "Trámites Internacionales", 'Solicitudes Legales <span class="text-accent">en Línea</span>',
        "Visas, pasaportes, antecedentes penales, apostillas y poderes para venezolanos en el país y en el exterior.",
        seccion("Solicitudes Disponibles", f'                <div class="row">\n{tarjetas}\n                </div>'))

    for url, contenido in paginas.items():
        destino = ruta(*url.strip("/").split("/"))
        os.makedirs(destino, exist_ok=True)
        # misma hoja de estilos / script que el resto de subpáginas
        for f in ("styles.css", "script.js"):
            dst = os.path.join(destino, f)
            if not os.path.exists(dst):
                shutil.copyfile(ruta("estados", PLANTILLA_ESTADO, f), dst)
        destino_html = os.path.join(destino, "index.html")
        if not os.path.exists(destino_html) or "<!-- GENERADO_POR_BUILD -->" in leer(destino_html):
            escribir(destino_html, contenido.replace("<body>", "<body>\n    <!-- GENERADO_POR_BUILD -->", 1))


# ==========================================================================
# 3. Post-proceso de todas las páginas
# ==========================================================================
def menu():
    serv = "\n".join(f'                        <a href="{u}" class="dropdown-item{" fw-bold" if i == 0 else ""}">{n}</a>'
                     for i, (n, u) in enumerate(SERVICIOS[:6]))
    serv_m = "\n".join(f'                <a href="{u}" class="mobile-dropdown-item{" fw-bold" if i == 0 else ""}">{n}</a>'
                       for i, (n, u) in enumerate(SERVICIOS[:6]))
    tram = [("Trámites en línea (todos)", "/tramites-en-linea/"), ("Trámites SAREN en Línea", "/tramites-en-linea/saren/"),
            ("Registro Civil", "/tramites-en-linea/registro-civil/"), ("Trámites Notariales", "/tramites-en-linea/notarias/"),
            ("Solicitudes Legales", "/tramites-en-linea/solicitudes/")]
    tr = "\n".join(f'                        <a href="{u}" class="dropdown-item">{n}</a>' for n, u in tram)
    tr_m = "\n".join(f'                <a href="{u}" class="mobile-dropdown-item">{n}</a>' for n, u in tram)
    est_orden = sorted(ESTADOS.items(), key=lambda kv: (kv[0] == "distrito-capital", kv[1][0]))
    es = "\n".join(f'                        <a href="/estados/{s}/" class="dropdown-item">{v[0]}</a>' for s, v in est_orden)
    es_m = "\n".join(f'                <a href="/estados/{s}/" class="mobile-dropdown-item">{v[0]}</a>' for s, v in est_orden)
    nos = [("Quiénes Somos", "/quienes-somos/"), ("Preguntas Frecuentes", "/#preguntas-frecuentes"),
           ("Contáctanos", "#contacto"), ("Política de Privacidad", "/politica-de-privacidad/"),
           ("Tratamiento de Datos", "/tratamiento-de-datos/")]
    no = "\n".join(f'                        <a href="{u}" class="dropdown-item">{n}</a>' for n, u in nos)
    no_m = "\n".join(f'                <a href="{u}" class="mobile-dropdown-item">{n}</a>' for n, u in nos)
    wa = f"https://wa.me/584245112587?text={WA_GENERIC}"

    def dd(titulo, href, items):
        return f"""                <div class="dropdown">
                    <a href="{href}" class="nav-link dropdown-toggle">
                        {titulo} <span style="margin-left: 5px;">▼</span>
                    </a>
                    <div class="dropdown-menu">
{items}
                    </div>
                </div>
"""

    def ddm(titulo, id_, items):
        return f"""        <div class="mobile-dropdown">
            <div class="mobile-dropdown-toggle" data-target="{id_}">
                {titulo} <span>▼</span>
            </div>
            <div class="mobile-dropdown-menu" id="{id_}">
{items}
            </div>
        </div>
"""
    return f"""<!-- ========== MENÚ COMPLETO ========== -->
    <nav class="main-nav">
        <div class="nav-container">
            <!-- Logo -->
            <a href="/" class="logo">
                <div class="logo-img">AV</div>
                <div>
                    <div class="logo-text">ABOGADOS VALENCIA</div>
                    <div class="logo-subtext">BUFETE ESPECIALIZADO EN DERECHO CIVIL</div>
                </div>
            </a>

            <!-- Menú Desktop -->
            <div class="desktop-menu">
                <a href="/" class="nav-link">Inicio</a>
{dd("Servicios Legales", "/#servicios", serv)}{dd("Trámites en Línea", "/tramites-en-linea/", tr)}{dd("Estados de Venezuela", "/estados-venezuela/", es)}{dd("Nosotros", "/quienes-somos/", no)}
                <!-- WhatsApp -->
                <a href="{wa}" class="whatsapp-btn">
                    <span>📱</span> WhatsApp
                </a>
            </div>

            <!-- Botón Hamburguesa -->
            <button class="mobile-menu-toggle" id="mobileMenuToggle" aria-label="Abrir menú">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
    </nav>

    <!-- Menú Móvil -->
    <div class="mobile-menu" id="mobileMenu">
        <a href="/" class="mobile-nav-link">Inicio</a>
{ddm("Servicios Legales", "servicios-mobile", serv_m)}{ddm("Trámites en Línea", "tramites-mobile", tr_m)}{ddm("Estados de Venezuela", "estados-mobile", es_m)}{ddm("Nosotros", "nosotros-mobile", no_m)}
        <!-- WhatsApp Móvil -->
        <div class="mobile-whatsapp">
            <a href="{wa}" class="whatsapp-btn">
                <span>📱</span> WhatsApp
            </a>
        </div>
    </div>

    <!-- Overlay para cerrar menú -->
    <div class="overlay" id="overlay"></div>
    """


WA_SNIPPET = """<!-- WA_PAGE_ID_SNIPPET -->
<script>
/* Identifica los mensajes de WhatsApp que llegan desde esta web:
   todos los mensajes terminan con "g33". Los enlaces genéricos se
   reemplazan por un mensaje con el título de la página. */
document.addEventListener("DOMContentLoaded", function() {
  var TAG = "g33";
  var cleanTitle = (document.title || "Pagina Web").replace(/[|\\-–]/g, " ").replace(/\\s+/g, " ").trim();
  var genericId = "estoy%20escribiendo%20desde%20la%20pagina%20web%20estoy%20interesado%20en%20uno%20de%20tus%20servicios";
  var pageMsg = "estoy escribiendo desde la pagina web (" + cleanTitle + ") estoy interesado en uno de tus servicios " + TAG;
  document.querySelectorAll('a[href*="wa.me/584245112587"]').forEach(function(link) {
    var href = link.getAttribute("href") || "";
    if (href.indexOf("?text=") === -1 || href.indexOf(genericId) !== -1) {
      link.setAttribute("href", "https://wa.me/584245112587?text=" + encodeURIComponent(pageMsg));
      return;
    }
    var text = href.split("?text=")[1];
    try { text = decodeURIComponent(text); } catch (e) {}
    if (!/(^|\\s)g33$/.test(text.trim())) {
      link.setAttribute("href", href + "%20" + TAG);
    }
  });
});
</script>
"""

ESTILOS = """<!-- ESTILOS_BUILD -->
    <style>
        .footer-legal a, #tramites-saren-en-linea a:not(.btn), .pagina-institucional a:not(.btn),
        .contact-section a:not(.btn) { color: #D4AF37; }
        .footer-legal a:hover, #tramites-saren-en-linea a:not(.btn):hover,
        .pagina-institucional a:not(.btn):hover { color: #F4D03F; }
    </style>
"""

GTAG = f"""<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', '{GA_ID}');
</script>
"""


def seccion_saren(estado=None):
    donde = f" en {estado}" if estado else " en toda Venezuela"
    texto_wa = f"Hola, quiero solicitar trámites SAREN en línea{(' en ' + estado) if estado else ''}"
    return f"""<!-- SAREN_EN_LINEA_INICIO -->
    <section class="py-5 bg-dark" id="tramites-saren-en-linea">
        <div class="container">
            <h2 class="section-title" data-aos="fade-up">Trámites SAREN en Línea{donde}</h2>
            <div class="row align-items-center" data-aos="fade-up">
                <div class="col-lg-8">
                    <p>Gestionamos por usted los <strong>trámites SAREN en línea</strong> (Servicio Autónomo de Registros y Notarías){donde}: registro de usuario, planillas, citas, pagos y seguimiento hasta la entrega del documento.</p>
                    <ul class="service-features">
                        <li>Apostilla y legalización de documentos en línea</li>
                        <li>Citas SAREN para registros y notarías</li>
                        <li>Poderes, autenticaciones y documentos notariales</li>
                        <li>Partidas y actas del Registro Civil</li>
                    </ul>
                </div>
                <div class="col-lg-4 text-center">
                    <a href="/tramites-en-linea/saren/" class="btn btn-outline-primary btn-lg w-100 mb-2">Ver Trámites SAREN en Línea</a>
                    <a href="{wa_link(texto_wa).replace('%20' + WA_TAG, '')}" class="btn btn-primary btn-lg w-100"><i class="fab fa-whatsapp me-2"></i> Solicitar por WhatsApp</a>
                </div>
            </div>
        </div>
    </section>
    <!-- SAREN_EN_LINEA_FIN -->

    """


def seccion_resenas():
    r = NEGOCIO["google_resena"]
    return f"""<!-- RESENAS_GOOGLE_INICIO -->
    <section class="py-5 bg-dark pagina-institucional" id="opiniones-google">
        <div class="container text-center">
            <h2 class="section-title" data-aos="fade-up">Opiniones en Google</h2>
            <p class="fs-4 mb-1"><strong>{NEGOCIO['google_calificacion']}</strong> <span style="color:#D4AF37">★★★★★</span></p>
            <p class="mb-4">{NEGOCIO['google_opiniones']} opiniones en nuestro perfil de Google · Abogados en Barinas desde {NEGOCIO['anio_apertura']}</p>
            <blockquote class="mb-4">
                <p class="fs-5">“{r['texto']}”</p>
                <footer class="small">— {r['autor']} · {r['detalle']}</footer>
            </blockquote>
            <a href="{NEGOCIO['google_maps']}" class="btn btn-outline-primary" target="_blank" rel="noopener">Ver opiniones en Google Maps</a>
        </div>
    </section>
    <!-- RESENAS_GOOGLE_FIN -->

    """


def direccion_texto():
    d = NEGOCIO["direccion"]
    return f"{d['streetAddress']}, {d['addressLocality']} {d['postalCode']}, {d['addressRegion']}"


def areas_texto():
    return [f"{c} {cp}, {e}".replace("  ", " ").strip(", ") if c else e
            for c, cp, e in NEGOCIO["areas_servicio"]]


def pie_legal():
    enlaces = [("Quiénes Somos", "/quienes-somos/"), ("Trámites SAREN en Línea", "/tramites-en-linea/saren/"),
               ("Estados", "/estados-venezuela/"), ("Política de Privacidad", "/politica-de-privacidad/"),
               ("Tratamiento de Datos", "/tratamiento-de-datos/"), ("Google Maps", NEGOCIO["google_maps"])]
    externo = ' target="_blank" rel="noopener"'
    a = " · ".join(f'<a href="{u}"{externo if u.startswith("http") else ""}>{n}</a>' for n, u in enlaces)
    return f'<!-- PIE_LEGAL --><p class="mb-2 small footer-legal">{a}</p>\n                '


def url_de(archivo):
    rel = os.path.relpath(os.path.dirname(archivo), ROOT).replace(os.sep, "/")
    return "/" if rel == "." else f"/{rel}/"


def schema(url, titulo, descripcion, estado_slug=None):
    org_id = BASE_URL + "/#organizacion"
    direccion = {k: v for k, v in NEGOCIO["direccion"].items() if v}
    direccion["@type"] = "PostalAddress"
    org = {
        "@type": ["LegalService", "LocalBusiness"],
        "@id": org_id,
        "name": NEGOCIO["nombre"],
        "alternateName": NEGOCIO["nombre_google"],
        "description": NEGOCIO["descripcion"],
        "foundingDate": NEGOCIO["fecha_apertura"],
        "knowsAbout": NEGOCIO["categorias"] + ["Trámites SAREN en línea", "Notarías", "Registro Civil",
                                               "Registro mercantil", "Registro inmobiliario", "Divorcios",
                                               "Sucesiones y herencias", "Poderes", "Venta de vehículos"],
        "url": BASE_URL + "/",
        "telephone": NEGOCIO["telefono"],
        "image": NEGOCIO["imagen"],
        "logo": NEGOCIO["logo"],
        "priceRange": "$$",
        "address": direccion,
        "hasMap": NEGOCIO["google_maps"],
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": "Entrada accesible para sillas de ruedas",
                            "value": NEGOCIO["accesible_silla_ruedas"]}],
        "sameAs": [NEGOCIO["google_maps"], NEGOCIO["facebook"]],
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": h["dias"], "opens": h["abre"], "closes": h["cierra"]}
            for h in NEGOCIO["horario"]],
        "contactPoint": [{"@type": "ContactPoint", "telephone": t, "contactType": "customer service",
                          "areaServed": "VE", "availableLanguage": ["es"]}
                         for t in (NEGOCIO["telefono"], NEGOCIO["telefono2"])],
        "areaServed": [{"@type": "Country", "name": "Venezuela"}] + [
            {"@type": "City", "name": f"{c}, {e}, Venezuela"} if c else {"@type": "State", "name": f"{e}, Venezuela"}
            for c, cp, e in NEGOCIO["areas_servicio"]],
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": "Servicios legales",
            "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "url": BASE_URL + u}}
                                for n, u in SERVICIOS]},
    }
    migas = [{"@type": "ListItem", "position": 1, "name": "Inicio", "item": BASE_URL + "/"}]
    partes = [p for p in url.strip("/").split("/") if p]
    nombres_seccion = {"estados": ("Estados de Venezuela", "/estados-venezuela/"),
                       "servicios": ("Servicios", "/#servicios"),
                       "tramites-en-linea": ("Trámites en Línea", "/tramites-en-linea/")}
    if len(partes) == 2 and partes[0] in nombres_seccion:
        n, u = nombres_seccion[partes[0]]
        migas.append({"@type": "ListItem", "position": 2, "name": n, "item": BASE_URL + u})
    if partes:
        migas.append({"@type": "ListItem", "position": len(migas) + 1, "name": titulo.split("|")[0].split("–")[0].strip(),
                      "item": BASE_URL + url})
    grafo = [
        org,
        {"@type": "WebSite", "@id": BASE_URL + "/#website", "url": BASE_URL + "/", "name": NEGOCIO["nombre"],
         "inLanguage": "es-VE", "publisher": {"@id": org_id}},
        {"@type": "WebPage", "@id": BASE_URL + url + "#webpage", "url": BASE_URL + url, "name": titulo,
         "description": descripcion, "inLanguage": "es-VE", "isPartOf": {"@id": BASE_URL + "/#website"},
         "about": {"@id": org_id}, "dateModified": TODAY},
    ]
    if len(migas) > 1:
        grafo.append({"@type": "BreadcrumbList", "itemListElement": migas})
    if estado_slug:
        nombre, capital = ESTADOS[estado_slug][0], ESTADOS[estado_slug][1]
        grafo.append({"@type": "Service", "name": f"Abogados en {nombre}",
                      "serviceType": "Asesoría legal y trámites SAREN en línea",
                      "provider": {"@id": org_id}, "url": BASE_URL + url,
                      "areaServed": {"@type": "State", "name": f"{nombre}, Venezuela",
                                     "containsPlace": {"@type": "City", "name": capital}},
                      "hasOfferCatalog": {"@type": "OfferCatalog", "name": f"Trámites legales en {nombre}",
                                          "itemListElement": [
                                              {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{s} en {nombre}"}}
                                              for s in ["Trámites SAREN en línea", "Registro Civil", "Notarías",
                                                        "Apostillas y legalizaciones", "Visas y pasaportes"]]}})
    data = {"@context": "https://schema.org", "@graph": grafo}
    return ('<!-- SCHEMA_JSONLD -->\n    <script type="application/ld+json">\n'
            + json.dumps(data, ensure_ascii=False, indent=2) + "\n    </script>\n")


def fix_wa_href(m):
    url = html.unescape(m.group(1))
    if "?text=" not in url:
        url = WA_BASE + "?text=" + WA_GENERIC
    base, texto = url.split("?text=", 1)
    texto = texto.replace(" ", "%20")
    if not re.search(r"(^|%20|\+)g33$", texto):
        texto += "%20" + WA_TAG
    return f'href="{base}?text={texto}"'


def post_procesar(archivo):
    s = leer(archivo)
    url = url_de(archivo)
    partes = url.strip("/").split("/")
    estado = partes[1] if len(partes) == 2 and partes[0] == "estados" else None

    # Google Analytics en todas las páginas
    if GA_ID not in s:
        s = s.replace("<head>", "<head>\n" + GTAG, 1)

    # Menú unificado
    ini = s.index("<!-- ========== MENÚ COMPLETO ========== -->")
    fin = s.index("<!-- ========== FIN MENÚ ========== -->")
    s = s[:ini] + menu() + s[fin:]

    # H1 y título estructurados en landing de estado: "Abogados en <Estado>"
    if estado:
        nombre, capital = ESTADOS[estado][0], ESTADOS[estado][1]
        s = re.sub(r'<h1 class="hero-title">.*?</h1>',
                   f'<h1 class="hero-title">Abogados en <span class="text-accent">{nombre}</span> – '
                   f'Trámites SAREN en Línea, Registro Civil y Notarías</h1>', s, count=1, flags=re.S)
        s = re.sub(r"<title>.*?</title>",
                   f"<title>Abogados en {nombre}, Venezuela | Trámites SAREN en Línea, Registro Civil y Notarías | Abogados Valencia</title>",
                   s, count=1, flags=re.S)
        # Imagen rota (ruta sin carpeta images/)
        s = s.replace('src="logo-abogados-en-venezuela', 'src="images/logo-abogados-en-venezuela')

    # Sección "Trámites SAREN en Línea" (excepto en su propia página)
    s = re.sub(r"<!-- SAREN_EN_LINEA_INICIO -->.*?<!-- SAREN_EN_LINEA_FIN -->\s*", "", s, flags=re.S)
    if url != "/tramites-en-linea/saren/":
        nombre_estado = ESTADOS[estado][0] if estado else None
        s = s.replace('<section class="contact-section" id="contacto">',
                      seccion_saren(nombre_estado) + '<section class="contact-section" id="contacto">', 1)

    # WhatsApp: "g33" al final de todos los mensajes
    s = re.sub(r'href="(https://wa\.me/584245112587[^"]*)"', fix_wa_href, s)
    s = re.sub(r"<!-- WA_PAGE_ID_SNIPPET -->\s*<script>.*?</script>\s*", "", s, flags=re.S)
    s = s.replace("</body>", WA_SNIPPET + "</body>", 1)

    # Pie: enlaces legales, año y horario consistentes con el perfil
    s = re.sub(r"<!-- PIE_LEGAL -->.*?\n\s*", "", s)
    s = s.replace('<div class="footer-bottom">\n                <p class="mb-0">',
                  '<div class="footer-bottom">\n                ' + pie_legal() + '<p class="mb-0">', 1)
    s = re.sub(r"&copy; (?:20\d\d[–-])?20\d\d ", f"&copy; {NEGOCIO['anio_apertura']}–{YEAR} ", s)
    h = NEGOCIO["horario"][0]
    s = re.sub(r'<p>Lunes a Viernes 8:00 AM - 6:00 PM</p>(\s*<p>Sábados 9:00 AM - 1:00 PM</p>)?',
               lambda m: "<p>" + h["texto"] + "</p>", s)
    s = re.sub(r'<li><i class="fas fa-clock me-2"></i> Lunes a Viernes 8:00-18:00</li>'
               r'(\s*<li><i class="fas fa-clock me-2"></i> Sábados 9:00-13:00</li>)?',
               lambda m: '<li><i class="fas fa-clock me-2"></i> ' + h["corto"] + "</li>", s)

    # Dirección, teléfonos y redes del perfil de Google
    tel1, tel2 = NEGOCIO["telefono_visible"], NEGOCIO["telefono2_visible"]
    li_tel = '<li><i class="fas fa-phone me-2"></i> '
    li_dir = '<li><i class="fas fa-map-marker-alt me-2"></i> '
    s = re.sub(re.escape(li_tel + tel1 + "</li>") + r"(?!\s*" + re.escape(li_tel + tel2) + ")",
               lambda m: m.group(0) + "\n                            " + li_tel + tel2 + "</li>", s)
    s = re.sub(re.escape(li_tel + tel2 + "</li>") + r"(?!\s*<li><i class=\"fas fa-map-marker-alt me-2\"></i> Frente)",
               lambda m: m.group(0) + "\n                            " + li_dir + direccion_texto() + "</li>", s)
    s = s.replace(li_dir + "Sede en Barinas · Cobertura Nacional</li>", li_dir + "Cobertura Nacional</li>")
    s = s.replace("<p>" + tel1 + "</p>",
                  f'<p><a href="tel:{NEGOCIO["telefono"]}">{tel1}</a> · <a href="tel:{NEGOCIO["telefono2"]}">{tel2}</a></p>')
    s = re.sub(r"<p>(?:Sede en Barinas · )?Cobertura en todos los estados de Venezuela</p>",
               lambda m: f'<p>{direccion_texto()}</p>\n                                <p><a href="{NEGOCIO["google_maps"]}" target="_blank" rel="noopener">Cómo llegar (Google Maps)</a> · Cobertura en todos los estados de Venezuela</p>', s)
    s = s.replace('<a href="#" class="social-link"><i class="fab fa-facebook-f"></i></a>',
                  f'<a href="{NEGOCIO["facebook"]}" class="social-link" target="_blank" rel="noopener" aria-label="Facebook"><i class="fab fa-facebook-f"></i></a>')
    s = re.sub(r'\s*<a href="#" class="social-link"><i class="fab fa-instagram"></i></a>', "", s)

    # Reseñas de Google (portada, Quiénes Somos y Barinas)
    s = re.sub(r"<!-- RESENAS_GOOGLE_INICIO -->.*?<!-- RESENAS_GOOGLE_FIN -->\s*", "", s, flags=re.S)
    if url in ("/", "/quienes-somos/", "/estados/barinas/"):
        s = s.replace('<section class="contact-section" id="contacto">',
                      seccion_resenas() + '<section class="contact-section" id="contacto">', 1)

    # Estilos de los bloques añadidos por este script
    s = re.sub(r"[ \t]*<!-- ESTILOS_BUILD -->\s*<style>.*?</style>\n?", "", s, flags=re.S)
    s = s.replace("</head>", "    " + ESTILOS + "</head>", 1)

    # Schema.org
    s = re.sub(r"[ \t]*<!-- SCHEMA_JSONLD -->\s*<script type=\"application/ld\+json\">.*?</script>\n?", "", s, flags=re.S)
    titulo = html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1).strip())
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', s)
    desc = html.unescape(desc_m.group(1)) if desc_m else titulo
    s = s.replace("</head>", "    " + schema(url, titulo, desc, estado) + "</head>", 1)

    escribir(archivo, s)


# ==========================================================================
# 4. Sitemap y validación
# ==========================================================================
def paginas_html():
    out = []
    for d, _, files in os.walk(ROOT):
        if "/.git" in d or "/tools" in d:
            continue
        if "index.html" in files:
            out.append(os.path.join(d, "index.html"))
    return sorted(out)


def prioridad(url):
    if url == "/":
        return "1.00", "weekly"
    if url.startswith("/servicios/") or url == "/tramites-en-linea/saren/":
        return "0.90", "weekly"
    if url.startswith("/tramites-en-linea/") or url == "/estados-venezuela/":
        return "0.80", "monthly"
    if url.startswith("/estados/"):
        return "0.70", "monthly"
    return "0.50", "yearly"


def generar_sitemap():
    lineas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    urls = sorted((url_de(p) for p in paginas_html()), key=lambda u: (u != "/", u))
    for u in urls:
        pr, cf = prioridad(u)
        lineas += ["    <url>", f"        <loc>{BASE_URL}{u}</loc>", f"        <lastmod>{TODAY}</lastmod>",
                   f"        <changefreq>{cf}</changefreq>", f"        <priority>{pr}</priority>", "    </url>"]
    lineas.append("</urlset>\n")
    escribir(ruta("sitemap.xml"), "\n".join(lineas))


def validar():
    errores = []
    paginas = paginas_html()
    urls = {url_de(p) for p in paginas}
    for p in paginas:
        s = leer(p)
        u = url_de(p)
        rel = os.path.relpath(p, ROOT)
        if len(re.findall(r"<h1[\s>]", s)) != 1:
            errores.append(f"{rel}: debe tener exactamente un <h1>")
        can = re.search(r'<link rel="canonical" href="([^"]*)"', s)
        if not can or can.group(1) != BASE_URL + u:
            errores.append(f"{rel}: canonical incorrecto ({can.group(1) if can else 'falta'})")
        for href in re.findall(r'href="(/[^"#]*)', s):
            destino = href.split("?")[0]
            if destino.endswith("/") and destino not in urls:
                errores.append(f"{rel}: enlace roto {href}")
            elif not destino.endswith("/") and not os.path.exists(ruta(destino.lstrip("/"))):
                errores.append(f"{rel}: recurso inexistente {href}")
        for src in re.findall(r'src="([^"]+)"', s):
            if not src.startswith(("http", "data:", "/")) and not os.path.exists(os.path.join(os.path.dirname(p), src)):
                errores.append(f"{rel}: recurso inexistente {src}")
        for wa in re.findall(r'href="(https://wa\.me/[^"]*)"', s):
            if not wa.endswith("%20" + WA_TAG):
                errores.append(f"{rel}: WhatsApp sin {WA_TAG}: {wa}")
        m = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
        if not m:
            errores.append(f"{rel}: falta schema JSON-LD")
        else:
            try:
                json.loads(m.group(1))
            except ValueError as e:
                errores.append(f"{rel}: JSON-LD inválido: {e}")
        if u.startswith("/estados/"):
            slug = u.strip("/").split("/")[1]
            nombre = ESTADOS[slug][0]
            h1 = re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S).group(1))
            if not h1.startswith(f"Abogados en {nombre}"):
                errores.append(f"{rel}: H1 debe empezar por 'Abogados en {nombre}'")
            cuerpo = s[s.index("FIN MENÚ"):]
            cuerpo = re.sub(r"<!-- SCHEMA_JSONLD -->.*?</script>", "", cuerpo, flags=re.S)
            if slug != "cojedes" and "Cojedes" in cuerpo:
                errores.append(f"{rel}: contiene texto de otro estado (Cojedes)")
        if f"&copy; {NEGOCIO['anio_apertura']}–{YEAR}" not in s:
            errores.append(f"{rel}: copyright distinto de {NEGOCIO['anio_apertura']}–{YEAR}")
        if re.search(r"Lunes a Viernes|Sábados 9:00", s):
            errores.append(f"{rel}: horario distinto del perfil de Google (24 horas)")
        if "tramites-en-linea/saren/" not in s:
            errores.append(f"{rel}: falta enlace a Trámites SAREN en Línea")
    for slug in ESTADOS:
        if f"/estados/{slug}/" not in urls:
            errores.append(f"falta la landing /estados/{slug}/")
    for req in ("/quienes-somos/", "/politica-de-privacidad/", "/tratamiento-de-datos/"):
        if req not in urls:
            errores.append(f"falta la página {req}")
    sm = leer(ruta("sitemap.xml"))
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    for u in urls:
        if BASE_URL + u not in locs:
            errores.append(f"sitemap.xml: falta {u}")
    for loc in locs:
        if loc[len(BASE_URL):] not in urls:
            errores.append(f"sitemap.xml: URL sin página {loc}")
    return errores, len(paginas)


def main():
    solo_validar = "--check" in sys.argv
    if not solo_validar:
        for slug in GENERAR_DESDE_PLANTILLA:
            generar_estado(slug)
        generar_paginas_institucionales()
        for p in paginas_html():
            post_procesar(p)
        generar_sitemap()
    errores, n = validar()
    for e in errores:
        print("ERROR:", e)
    print(f"{n} páginas revisadas, {len(errores)} errores")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
