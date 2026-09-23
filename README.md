# Abogados Valencia – Sitio web

Sitio estático (HTML + Bootstrap) publicado en Cloudflare Pages:
<https://abogadosvalencia.pages.dev/>

Perfil de Google Business: <https://maps.app.goo.gl/SuvKMZ2aup2iWXyV6>

## Estructura

| Ruta | Contenido |
|------|-----------|
| `/` | Página principal |
| `/servicios/*/` | Derecho civil, registros y notarías, trámites SAREN, documentos legales, contratos |
| `/tramites-en-linea/` | Índice de trámites en línea |
| `/tramites-en-linea/saren/` | **Trámites SAREN en línea** |
| `/tramites-en-linea/registro-civil/`, `/notarias/`, `/solicitudes/` | Otros trámites en línea |
| `/estados-venezuela/` | Índice de los 24 estados |
| `/estados/<estado>/` | Landing por estado: H1 `Abogados en <Estado> – …` |
| `/quienes-somos/` | Quiénes somos |
| `/politica-de-privacidad/` | Política de privacidad |
| `/tratamiento-de-datos/` | Tratamiento de datos personales |
| `sitemap.xml`, `robots.txt` | SEO |

Cada carpeta tiene su propio `index.html`, `styles.css` y `script.js`.

## Script de construcción y validación

Todos los cambios transversales los aplica `tools/build_site.py` (Python 3, sin dependencias):

```bash
python3 tools/build_site.py          # aplica los cambios, regenera sitemap.xml y valida
python3 tools/build_site.py --check  # solo valida (útil antes de publicar)
```

Se puede ejecutar varias veces sin duplicar nada. Hace lo siguiente:

- **WhatsApp:** todos los mensajes que salen de la web terminan con **`g33`**, para identificar
  en WhatsApp los contactos que llegan desde el sitio. Los enlaces genéricos incluyen además el
  título de la página de origen, por ejemplo:
  `estoy escribiendo desde la pagina web (Abogados en Lara, Venezuela …) estoy interesado en uno de tus servicios g33`.
  El `g33` está escrito en el HTML y un pequeño script (`WA_PAGE_ID_SNIPPET`) lo garantiza en el navegador.
- **Landing de estados:** genera las que faltaban y las que eran copias de Cojedes, usando
  `estados/apure/` como plantilla con la capital y los municipios de cada estado.
  El H1 y el `<title>` siguen el formato `Abogados en <Estado>`.
- **Menú unificado** en todas las páginas, sin enlaces rotos, con *Trámites SAREN en Línea* y
  la sección *Nosotros* (Quiénes Somos, Política de Privacidad, Tratamiento de Datos).
- **Servicio "Trámites SAREN en Línea"** agregado en todas las páginas (bloque antes de Contacto).
- **Schema.org (JSON-LD):** `LegalService`/`LocalBusiness`, `WebSite`, `WebPage`, `BreadcrumbList`
  y, en los estados, `Service` con `areaServed`.
- **Datos consistentes:** teléfono, horario, año del copyright, enlaces legales en el pie y
  Google Analytics (`G-RFW5F7YBBR`) en todas las páginas.
- **sitemap.xml** regenerado con todas las páginas y `lastmod` del día.
- **Validación:** un solo H1 por página, canonical correcto, enlaces internos y recursos
  existentes, `g33` en todos los enlaces de WhatsApp, JSON-LD válido, sitemap completo y
  ningún texto de Cojedes en otros estados.

### Datos del negocio (NAP)

Los datos del negocio están en un solo lugar: el diccionario `NEGOCIO` al inicio de
`tools/build_site.py`. Deben coincidir **exactamente** con el perfil de Google Business:

- Nombre: Abogados Valencia. El nombre completo del perfil va en `alternateName`: "Abogados Valencia ⚖️ | 🟢 Trámites de Notaría y Registro en Barinas - Civil y Familia"
- Categoría principal: Abogado (también: Servicios legales, Abogado civil, Abogado de derecho de familia, Abogado general)
- Dirección: Frente al Registro Público Inmobiliario, C.C Sabana Grande Avenida 23 de Enero, Barinas 5201, Barinas. Entrada accesible para sillas de ruedas
- Teléfonos: 0424-5112587 (principal y WhatsApp) y 0412-6015769
- Facebook: https://www.facebook.com/Abogadosenbarinas
- Horario: abierto las 24 horas, todos los días
- Fecha de apertura: 16 de marzo de 2010 (el copyright usa `© 2010–<año actual>`)
- Áreas de servicio: Barinas, Barinitas, Barrancas, La Luz, Pedraza, Socopó, Sabaneta, Valencia,
  Ciudad Guayana, San Cristóbal, Caracas, Lara, Miranda y Guárico
- Calificación en Google: 5.0 (10 opiniones). Se muestra en la portada, en Quiénes Somos y en
  Barinas, pero no va en el schema, porque Google no acepta como rich result las reseñas que el
  propio negocio publica sobre sí mismo.

Si algo cambia en el perfil de Google (horario, dirección, teléfono), edítalo en `NEGOCIO` y
ejecuta `python3 tools/build_site.py`.

## Notas

- `_redirects.txt` **no lo usa** Cloudflare Pages (el archivo tendría que llamarse `_redirects`).
  No lo renombres tal como está: la regla `/* /index.html 200` haría que cualquier URL
  inexistente mostrara la portada (soft 404).
- `google7a5c4682e9b25d4f.html` es la verificación de Google Search Console.
