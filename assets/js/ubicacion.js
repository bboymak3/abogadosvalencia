// Generado por tools/generar_landings.py
// Muestra en la portada un acceso a la página del estado desde el que se
// conecta el visitante. La ubicación la da Cloudflare (functions/api/ubicacion.js).
// No redirige: si no hay datos o el estado no tiene página, no se muestra nada.
(function () {
    var ESTADOS = {"Z": {"slug": "amazonas", "nombre": "Amazonas"}, "B": {"slug": "anzoategui", "nombre": "Anzoátegui"}, "C": {"slug": "apure", "nombre": "Apure"}, "D": {"slug": "aragua", "nombre": "Aragua"}, "E": {"slug": "barinas", "nombre": "Barinas"}, "F": {"slug": "bolivar", "nombre": "Bolívar"}, "G": {"slug": "carabobo", "nombre": "Carabobo"}, "H": {"slug": "cojedes", "nombre": "Cojedes"}, "Y": {"slug": "delta-amacuro", "nombre": "Delta Amacuro"}, "I": {"slug": "falcon", "nombre": "Falcón"}, "J": {"slug": "guarico", "nombre": "Guárico"}, "K": {"slug": "lara", "nombre": "Lara"}, "L": {"slug": "merida", "nombre": "Mérida"}, "M": {"slug": "miranda", "nombre": "Miranda"}};
    var NOMBRES = {};
    Object.keys(ESTADOS).forEach(function (k) { NOMBRES[normalizar(ESTADOS[k].nombre)] = ESTADOS[k]; });

    function normalizar(t) {
        return (t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/^estado\s+/, "").trim();
    }

    var caja = document.getElementById("tu-estado");
    if (!caja || !window.fetch) return;

    fetch("/api/ubicacion", { headers: { "Accept": "application/json" } })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) {
            if (!d || d.pais !== "VE") return;
            var estado = ESTADOS[(d.codigoRegion || "").toUpperCase()] || NOMBRES[normalizar(d.region)];
            if (!estado) return;
            var enlace = caja.querySelector(".ubicacion-card");
            enlace.href = "/estados/" + estado.slug + "/";
            caja.querySelector(".ubicacion-estado").textContent = estado.nombre;
            caja.hidden = false;
            if (window.gtag) gtag("event", "ubicacion_estado", { estado: estado.slug });
        })
        .catch(function () {});
})();
