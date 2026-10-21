// Cloudflare Pages Function: GET /api/ubicacion
// Devuelve el país y el estado (región) desde donde se conecta el visitante,
// según la geolocalización por IP que Cloudflare añade a cada petición
// (request.cf). No guarda nada ni devuelve la IP.
export function onRequestGet({ request }) {
    const cf = request.cf || {};
    const datos = {
        pais: cf.country || "",
        region: cf.region || "",
        codigoRegion: cf.regionCode || "",
    };
    return new Response(JSON.stringify(datos), {
        headers: {
            "Content-Type": "application/json; charset=utf-8",
            "Cache-Control": "private, no-store",
        },
    });
}
