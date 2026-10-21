# Abogados Valencia

Sitio estático de **Abogados Valencia** (https://abogadosvalencia.pages.dev), publicado en Cloudflare Pages desde la rama `main`.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `/` (`index.html`) | Portada |
| `/servicios/*/` | Páginas de servicios (derecho civil, contratos, documentos legales, registros y notarías, trámites SAREN) |
| `/tramites-en-linea/*/` | Trámites en línea (SAREN, registro civil, notarías) |
| `/estados/<estado>/` | Una página por estado (14): municipios plegados, FAQ y datos estructurados propios |
| `/abogados/` | Índice de municipios y parroquias del estado Carabobo |
| `/abogados/<municipio>/` | Landing por municipio de Carabobo (14) |
| `/abogados/<municipio>/<parroquia>/` | Landing por parroquia de Carabobo (38) |
| `/saren-en-linea/` | Servicio destacado: trámites, recaudos, paso a paso y FAQ |
| `/informacion-legal/preguntas-frecuentes/` | Qué es un abogado, preguntas frecuentes, documentos para el exterior y guía de áreas y trámites |
| `/api/ubicacion` | Función de Cloudflare Pages (`functions/api/ubicacion.js`): país y estado del visitante |
| `404.html` | Página de error con el mismo estilo |

Archivos del sitio:

- `assets/css/ios.css`: capa de estilo iOS (se carga después de `styles.css`, solo refina).
- `assets/css/landings.css`: componentes de las páginas nuevas y de los bloques plegados.
- `assets/icons/`: favicon SVG/PNG, apple-touch-icon e iconos PWA (192, 512 y maskable).
- `assets/js/ubicacion.js` (generado): en la portada muestra un acceso a la página del estado desde el que se conecta el visitante. Usa `/api/ubicacion` (geolocalización por IP de Cloudflare, `request.cf`). No redirige ni guarda datos; si el estado no tiene página o la consulta falla, no muestra nada.
- `tools/fragmentos/`: contenido trasladado desde la portada (qué es un abogado, documentos para el exterior y directorio de áreas), del que se genera la página de preguntas frecuentes.
- `manifest.webmanifest`, `sitemap.xml`, `robots.txt`, `_headers` y `_redirects` (Cloudflare Pages).

## Herramientas (`tools/`)

Todo el contenido generado sale de `tools/datos.py`. Después de editarlo, ejecuta en este orden:

```bash
python3 tools/adaptar_estados.py    # textos propios de cada página de estado
python3 tools/generar_landings.py   # capa global, landings, SAREN, 404, sitemap, manifest, _headers, _redirects
python3 tools/generar_iconos.py     # solo si cambia el logotipo
```

- **`datos.py`**: datos del negocio (teléfono, WhatsApp, horario, Google Analytics), municipios y parroquias de Carabobo, municipios de cada estado (`ESTADOS_MUNICIPIOS`), capital, código ISO y ciudades de cada estado (`ESTADOS_INFO`), servicios y textos variables.
- **`adaptar_estados.py`**: reescribe solo el texto de `/estados/<estado>/` (title, meta description, H1, H2, introducciones, cobertura, ventajas, FAQ, CTA, contacto y pie) con redacciones distintas por estado. No toca la estructura, los menús, los botones ni los scripts.
- **`generar_landings.py`**: añade a todas las páginas existentes, entre marcadores `<!-- AÑADIDO:... -->`, las metaetiquetas (Open Graph, Twitter Card, geo, PWA), la barra inferior de Llamar/WhatsApp, el crédito del pie y los datos estructurados. También genera las landings, el índice, `/saren-en-linea/`, `404.html`, `sitemap.xml`, `manifest.webmanifest`, `_headers` y `_redirects`.

Los dos generadores son deterministas: volver a ejecutarlos no cambia nada si los datos no cambiaron.

## SEO y datos estructurados

- **Portada** (neutral, para toda Venezuela): Organization, WebSite, LegalService (areaServed: Venezuela y los estados con página, horario y catálogo de servicios), Service y FAQPage.
- **Preguntas frecuentes**: WebPage, BreadcrumbList y FAQPage.
- **Páginas de estado**: WebPage, LegalService (estado y sus municipios), Service, BreadcrumbList y FAQPage con las preguntas visibles de la página. Llevan `geo.region` con el código ISO 3166-2 del estado.
- **Landings de Carabobo**: WebPage, LegalService, Service, BreadcrumbList, FAQPage y HowTo.
- **Todas las páginas**: `canonical`, Open Graph, Twitter Card y `theme-color`. Todas las URL están en `sitemap.xml`, enlazado desde `robots.txt`.

## Contacto en la web

- Teléfono / WhatsApp: +58 424-5112587
- Pie de página: «Página web desarrollada por Grupo 360 Soluciones · Diseño por [makeseo.app](https://makeseo.app)»
