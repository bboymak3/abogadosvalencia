# -*- coding: utf-8 -*-
"""
Datos del proyecto para el generador de landings (tools/generar_landings.py).

Edita este archivo y vuelve a ejecutar:
    python3 tools/generar_landings.py

Todo el contenido generado sale de aquí: datos del negocio, municipios y
parroquias oficiales del estado Carabobo, servicios y textos variables.
No se incluyen direcciones, valoraciones ni reseñas.
"""

# ---------------------------------------------------------------------------
# Datos del negocio (tomados de la web existente)
# ---------------------------------------------------------------------------
SITIO = {
    "dominio": "https://abogadosvalencia.pages.dev",
    "nombre": "Abogados Valencia",
    "descripcion_corta": "Bufete especializado en derecho civil, familia y trámites SAREN en línea",
    "telefono_visible": "+58 424-5112587",
    "telefono_local": "0424-5112587",
    "telefono_e164": "+584245112587",
    "whatsapp": "584245112587",
    "ga_id": "G-RFW5F7YBBR",
    "estado": "Carabobo",
    "pais": "Venezuela",
    "codigo_region": "VE-G",  # ISO 3166-2 del estado Carabobo
    "logo": "/images/logo-abogados-en-venezuela-apure-barinas-valencia-caracas-zulia-lara-servicios-saren-en-linea.jpg",
    "imagen_og": "/images/logo-abogados-en-venezuela-apure-barinas-valencia-caracas-zulia-lara-servicios-saren-en-linea.jpg",
    "theme_color": "#000000",
    # Horario publicado en la sección de contacto de la portada
    "horario": [
        {"dias": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "abre": "08:00", "cierra": "18:00"},
        {"dias": ["Saturday"], "abre": "09:00", "cierra": "13:00"},
    ],
    "horario_texto": "Lunes a viernes de 8:00 a. m. a 6:00 p. m. y sábados de 9:00 a. m. a 1:00 p. m.",
    "servicio_destacado": "SAREN en línea",
    "credito_texto": "Página web desarrollada por Grupo 360 Soluciones",
    "credito_prefijo_enlace": "Diseño por",
    "credito_enlace_texto": "makeseo.app",
    "credito_enlace_url": "https://makeseo.app",
}

# ---------------------------------------------------------------------------
# Municipios y parroquias oficiales del estado Carabobo (14 municipios, 38 parroquias)
# "vecinos": municipios colindantes o cercanos, para los enlaces de "zonas cercanas".
# ---------------------------------------------------------------------------
MUNICIPIOS = [
    {"nombre": "Bejuma", "slug": "bejuma", "capital": "Bejuma",
     "zona": "el occidente montañoso del estado",
     "parroquias": ["Bejuma", "Canoabo", "Simón Bolívar"],
     "vecinos": ["montalban", "miranda", "juan-jose-mora"]},
    {"nombre": "Carlos Arvelo", "slug": "carlos-arvelo", "capital": "Güigüe",
     "zona": "la ribera sur del Lago de Valencia",
     "parroquias": ["Güigüe", "Belén", "Tacarigua"],
     "vecinos": ["valencia", "libertador", "los-guayos"]},
    {"nombre": "Diego Ibarra", "slug": "diego-ibarra", "capital": "Mariara",
     "zona": "la ribera norte del Lago de Valencia, hacia el límite con Aragua",
     "parroquias": ["Mariara", "Aguas Calientes"],
     "vecinos": ["san-joaquin", "guacara"]},
    {"nombre": "Guacara", "slug": "guacara", "capital": "Guacara",
     "zona": "el eje industrial del este de Carabobo",
     "parroquias": ["Guacara", "Ciudad Alianza", "Yagua"],
     "vecinos": ["san-diego", "los-guayos", "san-joaquin", "puerto-cabello"]},
    {"nombre": "Juan José Mora", "slug": "juan-jose-mora", "capital": "Morón",
     "zona": "la costa occidental del estado",
     "parroquias": ["Morón", "Urama"],
     "vecinos": ["puerto-cabello", "bejuma"]},
    {"nombre": "Libertador", "slug": "libertador", "capital": "Tocuyito",
     "zona": "el suroeste del área metropolitana de Valencia",
     "parroquias": ["Tocuyito", "Independencia"],
     "vecinos": ["valencia", "naguanagua", "carlos-arvelo", "miranda"]},
    {"nombre": "Los Guayos", "slug": "los-guayos", "capital": "Los Guayos",
     "zona": "el este del área metropolitana de Valencia",
     "parroquias": ["Los Guayos"],
     "vecinos": ["valencia", "san-diego", "guacara", "carlos-arvelo"]},
    {"nombre": "Miranda", "slug": "miranda", "capital": "Miranda",
     "zona": "el occidente del estado",
     "parroquias": ["Miranda"],
     "vecinos": ["bejuma", "montalban", "libertador"]},
    {"nombre": "Montalbán", "slug": "montalban", "capital": "Montalbán",
     "zona": "el extremo occidental del estado",
     "parroquias": ["Montalbán"],
     "vecinos": ["bejuma", "miranda"]},
    {"nombre": "Naguanagua", "slug": "naguanagua", "capital": "Naguanagua",
     "zona": "el norte del área metropolitana de Valencia",
     "parroquias": ["Naguanagua"],
     "vecinos": ["valencia", "san-diego", "libertador", "puerto-cabello"]},
    {"nombre": "Puerto Cabello", "slug": "puerto-cabello", "capital": "Puerto Cabello",
     "zona": "la costa central del estado",
     "parroquias": ["Bartolomé Salóm", "Democracia", "Fraternidad", "Goaigoaza",
                    "Juan José Flores", "Unión", "Borburata", "Patanemo"],
     "vecinos": ["juan-jose-mora", "naguanagua", "guacara"]},
    {"nombre": "San Diego", "slug": "san-diego", "capital": "San Diego",
     "zona": "el noreste del área metropolitana de Valencia",
     "parroquias": ["San Diego"],
     "vecinos": ["valencia", "naguanagua", "guacara", "los-guayos"]},
    {"nombre": "San Joaquín", "slug": "san-joaquin", "capital": "San Joaquín",
     "zona": "el este del estado, cerca del límite con Aragua",
     "parroquias": ["San Joaquín"],
     "vecinos": ["guacara", "diego-ibarra"]},
    {"nombre": "Valencia", "slug": "valencia", "capital": "Valencia",
     "zona": "la capital del estado",
     "parroquias": ["Candelaria", "Catedral", "El Socorro", "Miguel Peña", "Rafael Urdaneta",
                    "San Blas", "San José", "Santa Rosa", "Negro Primero"],
     "vecinos": ["naguanagua", "san-diego", "los-guayos", "libertador", "carlos-arvelo"]},
]

# ---------------------------------------------------------------------------
# Servicios (los mismos que ya ofrece la web). "url" enlaza a la página existente.
# ---------------------------------------------------------------------------
SERVICIOS = [
    {"nombre": "SAREN en línea", "icono": "fa-laptop-file", "url": "/saren-en-linea/",
     "texto": "Legalizaciones, autenticaciones, poderes, citas y seguimiento de trámites ante registros y notarías."},
    {"nombre": "Registros y notarías", "icono": "fa-landmark", "url": "/servicios/registros-notarias/",
     "texto": "Preparación y visado de documentos para su protocolización o autenticación."},
    {"nombre": "Documentos legales y poderes", "icono": "fa-file-signature", "url": "/servicios/documentos-legales/",
     "texto": "Redacción de poderes, declaraciones juradas, autorizaciones de viaje y otros documentos."},
    {"nombre": "Contratos", "icono": "fa-file-contract", "url": "/servicios/contratos/",
     "texto": "Compraventa, arrendamiento, opción a compra, préstamo y contratos de servicio."},
    {"nombre": "Derecho civil", "icono": "fa-balance-scale", "url": "/servicios/derecho-civil/",
     "texto": "Títulos supletorios, propiedad, obligaciones y reclamaciones civiles."},
    {"nombre": "Divorcios y derecho de familia", "icono": "fa-user-friends", "url": "/#nuevas-areas",
     "texto": "Divorcio de mutuo acuerdo, custodia, obligación de manutención y régimen de convivencia."},
    {"nombre": "Herencias y sucesiones", "icono": "fa-hand-holding-usd", "url": "/#categorias",
     "texto": "Declaratoria de herederos, declaración sucesoral y partición de bienes."},
    {"nombre": "Documentos para el exterior", "icono": "fa-plane-departure", "url": "/#info-barinas",
     "texto": "Copias certificadas, legalización y orientación para la apostilla de documentos."},
    {"nombre": "Derecho mercantil", "icono": "fa-building", "url": None,
     "texto": "Registro de firmas personales y compañías, actas de asamblea y cambios en la junta directiva."},
    {"nombre": "Derecho laboral", "icono": "fa-briefcase", "url": "/#nuevas-areas",
     "texto": "Cálculo y reclamo de prestaciones sociales, despidos y accidentes de trabajo."},
    {"nombre": "Accidentes y lesiones", "icono": "fa-car-crash", "url": "/#nuevas-areas",
     "texto": "Asesoría tras accidentes de tránsito y reclamaciones a aseguradoras."},
    {"nombre": "Derecho penal", "icono": "fa-gavel", "url": "/#nuevas-areas",
     "texto": "Asistencia en audiencias, medidas cautelares y recursos de apelación."},
]

# ---------------------------------------------------------------------------
# SAREN en línea: contenido de la landing dedicada
# ---------------------------------------------------------------------------
SAREN_TRAMITES = [
    ("Legalización de documentos", "Carga y seguimiento de actas, títulos y documentos que deben legalizarse por vía electrónica."),
    ("Autenticación de documentos", "Preparación y visado de documentos para su autenticación ante notaría."),
    ("Poderes generales y especiales", "Redacción del poder, revisión de datos y gestión de la cita para su otorgamiento."),
    ("Compraventa de inmuebles y vehículos", "Revisión de la tradición legal, redacción del documento y gestión ante el registro o notaría."),
    ("Registro de empresas y actas de asamblea", "Constitución de firmas personales y compañías, y registro de actas ante el registro mercantil."),
    ("Autorizaciones de viaje para menores", "Redacción de la autorización y orientación sobre los recaudos de ambos representantes."),
    ("Documentos para usar en el exterior", "Copias certificadas, legalización y orientación para la apostilla ante la Cancillería."),
    ("Solicitud y seguimiento de citas", "Registro en la plataforma, solicitud de la cita y seguimiento hasta la entrega."),
]

SAREN_RECAUDOS = [
    "Cédula de identidad laminada y vigente de cada otorgante.",
    "RIF vigente cuando el trámite lo exija.",
    "Documento redactado y visado por un abogado (cuando aplica).",
    "Documento de propiedad o documentos anteriores del bien (compraventas).",
    "Acta constitutiva y última acta de asamblea (trámites de empresas).",
    "Comprobante de pago de los aranceles y tasas oficiales.",
]

SAREN_PASOS = [
    ("Escríbenos", "Cuéntanos por WhatsApp qué trámite necesitas y desde dónde lo harás."),
    ("Revisamos tus documentos", "Te indicamos los recaudos exactos y revisamos los datos antes de cargar nada."),
    ("Preparamos y cargamos", "Redactamos o visamos el documento y lo registramos en la plataforma correspondiente."),
    ("Gestionamos la cita y el pago", "Te guiamos con la cita y con el pago de los aranceles oficiales."),
    ("Seguimiento hasta la entrega", "Te avisamos de cada avance hasta que el documento esté listo."),
]

SAREN_FAQ = [
    ("¿Ustedes son el SAREN?",
     "No. Somos abogados y gestores independientes. No somos el SAREN ni una oficina oficial del Estado; te ayudamos a preparar y gestionar tus trámites ante los registros y notarías."),
    ("¿Puedo hacer el trámite si estoy fuera de Venezuela?",
     "Muchos trámites pueden adelantarse a distancia. Te indicamos cuáles se pueden hacer en línea y cuáles exigen la presencia del otorgante o un apoderado en Venezuela."),
    ("¿Cuánto cuesta un trámite en el SAREN?",
     "Los aranceles oficiales dependen del tipo de trámite y de las tasas vigentes. Nuestros honorarios se acuerdan por separado y te los informamos antes de empezar."),
    ("¿Cuánto tarda una legalización o autenticación?",
     "Depende del tipo de documento, de la disponibilidad de citas y de la oficina. Te damos un estimado al revisar tu caso y te mantenemos informado."),
    ("¿Qué documentos necesito para empezar?",
     "Como mínimo, tu cédula de identidad vigente y el documento a tramitar. Según el caso, también el RIF, documentos de propiedad o actas de la empresa."),
]

# ---------------------------------------------------------------------------
# Textos variables para que cada landing tenga una introducción distinta.
# Marcadores: {lugar}, {municipio}, {capital}, {zona}, {estado}, {servicio}
# ---------------------------------------------------------------------------
INTROS_A = [
    "Si vives en {lugar} y necesitas un abogado para un trámite, un contrato o un problema legal, te atendemos por WhatsApp y por teléfono sin que tengas que perder el día en filas.",
    "En {lugar} cada vez más personas resuelven sus trámites legales a distancia. Nosotros revisamos tus documentos, te explicamos los pasos y te acompañamos hasta el final.",
    "¿Buscas un abogado en {lugar}? Te ayudamos con trámites de registros y notarías, documentos legales, divorcios, herencias y más, con atención directa por WhatsApp.",
    "Para los vecinos de {lugar}, ofrecemos asesoría legal clara y seguimiento de cada trámite, desde la primera consulta hasta la entrega del documento.",
    "Resolver un asunto legal en {lugar} no tiene por qué ser complicado. Te decimos qué necesitas, cuánto cuesta y cuánto puede tardar antes de empezar.",
    "Atendemos a personas y empresas de {lugar} que necesitan un abogado para trámites ante el SAREN, contratos, poderes y asuntos de familia.",
    "Desde {lugar} puedes consultarnos tu caso por WhatsApp: revisamos la documentación, te orientamos y gestionamos el trámite contigo.",
    "Si estás en {lugar}, o eres de allí y vives fuera del país, te ayudamos a preparar y gestionar tus documentos legales con seguimiento constante.",
]

INTROS_B = [
    "{lugar} forma parte del municipio {municipio}, en {zona}, y desde aquí coordinamos trámites ante los registros y notarías que correspondan a cada caso.",
    "Trabajamos con clientes de todo el municipio {municipio}, en {zona}, y adaptamos cada trámite a la oficina competente según tu documento.",
    "Como el municipio {municipio} está en {zona}, organizamos las citas y los traslados necesarios para que pierdas el menor tiempo posible.",
    "Nuestro trabajo en el municipio {municipio} se centra en evitar errores en los documentos, que son la causa más común de retrasos en registros y notarías.",
    "En el municipio {municipio}, en {zona}, atendemos tanto trámites sencillos como casos que requieren seguimiento judicial.",
]

INTROS_C = [
    "Nuestro servicio más solicitado es {servicio}: te ayudamos con legalizaciones, autenticaciones, poderes y citas.",
    "Destacamos la gestión de {servicio}, ideal si necesitas legalizar, autenticar o registrar un documento sin complicaciones.",
    "Si tu trámite es de {servicio}, revisamos tus recaudos antes de cargar la solicitud para evitar rechazos.",
    "Con {servicio} puedes adelantar gran parte del trámite a distancia; nosotros te guiamos en cada paso.",
]

FAQ_LOCAL = [
    ("¿Atienden a personas de {lugar}?",
     "Sí. Atendemos a personas y empresas de {lugar} y de todo el municipio {municipio} por WhatsApp y por teléfono, y coordinamos el trámite ante la oficina que corresponda."),
    ("¿Puedo hacer un trámite de {servicio} desde {lugar} sin ir a una oficina?",
     "Muchos pasos se pueden adelantar a distancia: revisión de documentos, redacción, registro en la plataforma y solicitud de la cita. Algunos actos exigen la presencia del otorgante, y te lo indicamos desde el principio."),
    ("¿Qué necesito para una consulta con un abogado en {lugar}?",
     "Solo escríbenos por WhatsApp con una breve descripción del caso. Si tienes documentos relacionados, puedes enviarnos fotos legibles para revisarlos."),
    ("¿Cuánto cuesta un abogado en {lugar}?",
     "Depende del tipo de trámite o caso. Te informamos los honorarios y los aranceles oficiales antes de empezar, sin compromiso."),
    ("¿Ayudan a venezolanos en el exterior con trámites en {lugar}?",
     "Sí. Si eres de {lugar} y vives fuera de Venezuela, te ayudamos con poderes, copias certificadas, legalizaciones y otros trámites que puedan gestionarse a distancia."),
]

PASOS_LANDING = [
    ("Consulta por WhatsApp", "Cuéntanos tu caso y desde dónde nos escribes."),
    ("Revisión de documentos", "Te indicamos los recaudos y revisamos lo que ya tienes."),
    ("Presupuesto claro", "Conoces los honorarios y los aranceles oficiales antes de empezar."),
    ("Gestión y seguimiento", "Preparamos el trámite y te informamos de cada avance."),
]
