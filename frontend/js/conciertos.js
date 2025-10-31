const API_BASE = "http://127.0.0.1:8000/api";
const ARTISTAS_URL = `${API_BASE}/artistas`;
const CONCIERTOS_URL = `${API_BASE}/conciertos`;

const LIMIT_ARTISTAS = 50;
const LIMIT_CONCIERTOS = 50; // queremos traernos bastantes conciertos de un jalón

// Elementos del DOM

const selectArtista = document.getElementById("selectArtista");

const artistaInfoSection = document.getElementById("artistaInfo");
const artistImage = document.getElementById("artistImage");
const artistName = document.getElementById("artistName");
const artistCountry = document.getElementById("artistCountry");
const artistPopularity = document.getElementById("artistPopularity");
const artistBio = document.getElementById("artistBio");

const listaConciertos = document.getElementById("listaConciertos");
const sinConciertosMsg = document.getElementById("sinConciertosMsg");

// modo oscuro 
const modoOscuroToggle = document.getElementById("modoOscuro");


// Leaflet map setup

let map = L.map("concertMap").setView([19.4326, -99.1332], 4); // vista inicial aproximada (México/US)
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
}).addTo(map);

let markerLayer = L.layerGroup().addTo(map);

// Estado en memoria

// guardamos todos los artistas que cargamos para no volver a pedir
let artistasCache = [];


// formatea fechas ISO a algo más legible
function formatearFecha(iso) {
    if (!iso) return "Fecha no disponible";
    const d = new Date(iso);
    // usamos hora local
    return d.toLocaleString("es-MX", {
        dateStyle: "medium",
        timeStyle: "short"
    });
}

// badge status
function renderStatusBadge(status) {
    if (!status) return "";
    const lower = status.toLowerCase();
    if (lower.includes("confirm")) {
        return `<span class="badge-status badge-confirmado">Confirmado</span>`;
    } else if (lower.includes("plan")) {
        return `<span class="badge-status badge-planeado">Planeado</span>`;
    }
    return `<span class="badge-status bg-secondary text-white">${status}</span>`;
}

// Cargar artistas (con paginación)

async function cargarArtistas() {
    let page = 1;
    let allArtists = [];
    let hasNext = true;

    while (hasNext) {
        const url = `${ARTISTAS_URL}?page=${page}&limit=${LIMIT_ARTISTAS}`;
        try {
            const res = await fetch(url);
            const json = await res.json();

            if (json.success && Array.isArray(json.data)) {
                allArtists = allArtists.concat(json.data);
            }

            hasNext = json.pagination?.has_next || false;
            page++;
        } catch (err) {
            console.error("Error cargando artistas:", err);
            break;
        }
    }

    artistasCache = allArtists;
    popularDropdownArtistas(allArtists);
}

// Llena el <select> con los artistas
function popularDropdownArtistas(artists) {
    selectArtista.innerHTML = `<option selected disabled>Selecciona un artista...</option>`;

    artists.forEach(art => {
        const opt = document.createElement("option");
        // necesitamos ID del artista para luego filtrar conciertos
        opt.value = art.id ?? art.artista_id ?? art.nombre;
        opt.textContent = art.nombre;
        opt.dataset.nombre = art.nombre;
        opt.dataset.imagen = art.imagen_url || "";
        opt.dataset.pais = art.pais || "";
        opt.dataset.popularidad = art.popularidad ?? "";
        opt.dataset.bio = art.biografia || "";
        selectArtista.appendChild(opt);
    });
}

// Evento: cambio de artista

selectArtista.addEventListener("change", async () => {
    const selectedOption = selectArtista.options[selectArtista.selectedIndex];

    const artistaId = selectedOption.value;
    const nombre = selectedOption.dataset.nombre;
    const imagen = selectedOption.dataset.imagen;
    const pais = selectedOption.dataset.pais;
    const popularidad = selectedOption.dataset.popularidad;
    const bio = selectedOption.dataset.bio;

    // 1. Pintar tarjeta del artista
    renderArtistaCard({ nombre, imagen, pais, popularidad, bio });

    // 2. Pedir conciertos de ese artista 
    const conciertos = await cargarConciertosPorArtista(artistaId);

    // 3. Poner marcadores en el mapa
    renderMarkers(conciertos, nombre);

    // 4. Poner lista de conciertos
    renderListaConciertos(conciertos, nombre);
});

// pinta la tarjeta con la info del artista
function renderArtistaCard({ nombre, imagen, pais, popularidad, bio }) {
    artistImage.src = imagen || "img/logo.png";
    artistImage.alt = nombre || "Artista";
    artistName.textContent = nombre || "Artista";
    artistCountry.textContent = pais || "—";
    artistPopularity.textContent = popularidad || "—";
    artistBio.textContent = bio || "Sin biografía";

    artistaInfoSection.style.display = "block";
}

// Cargar conciertos por artista

async function cargarConciertosPorArtista(artistaId) {
    let page = 1;
    let allConcerts = [];
    let hasNext = true;

    while (hasNext) {
        const url = `${CONCIERTOS_URL}?page=${page}&limit=${LIMIT_CONCIERTOS}&artista_id=${artistaId}`;
        try {
            const res = await fetch(url);
            const json = await res.json();

            if (json.success && Array.isArray(json.data)) {
                allConcerts = allConcerts.concat(json.data);
            }

            hasNext = json.pagination?.has_next || false;
            page++;
        } catch (err) {
            console.error("Error cargando conciertos:", err);
            break;
        }
    }

    return allConcerts;
}


// Mapa: render markers

function renderMarkers(conciertos, artistaNombre) {
    markerLayer.clearLayers();

    if (!conciertos || conciertos.length === 0) {
        // centrar a vista default si no hay conciertos
        map.setView([19.4326, -99.1332], 4);
        return;
    }

    // bounds para ajustar zoom al conjunto de puntos
    const bounds = [];

    conciertos.forEach(c => {
        // necesitamos lat/long del concierto
        if (c.latitud && c.longitud) {
            const marker = L.marker([c.latitud, c.longitud]);

            // popup
            const fechaStr = formatearFecha(c.fecha);
            // para "precio" usamos ingresos_taquilla como aproximación
            const precioStr = c.ingresos_taquilla
                ? `$${c.ingresos_taquilla.toLocaleString("es-MX")}`
                : "N/D";

            marker.bindPopup(`
        <div style="min-width:180px">
          <strong>${artistaNombre}</strong><br/>
          <span>${c.nombre_evento || "Evento"}</span><br/>
          <span>${c.ciudad || "Ciudad"}, ${c.pais || ""}</span><br/>
          <span>${fechaStr}</span><br/>
          <span><b>Precio / Taquilla:</b> ${precioStr}</span>
        </div>
      `);

            marker.addTo(markerLayer);
            bounds.push([c.latitud, c.longitud]);
        }
    });

    if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [30, 30] });
    }
}


// Lista lateral de conciertos

function renderListaConciertos(conciertos, artistaNombre) {
    listaConciertos.innerHTML = "";
    if (!conciertos || conciertos.length === 0) {
        listaConciertos.innerHTML = `
      <div class="text-center text-muted p-4">
        No hay conciertos programados para este artista.
      </div>
    `;
        return;
    }

    conciertos.forEach(c => {
        const fechaStr = formatearFecha(c.fecha);
        const statusBadge = renderStatusBadge(c.status);

        const ingresosStr = c.ingresos_taquilla
            ? `$${c.ingresos_taquilla.toLocaleString("es-MX")}`
            : "N/D";

        const costosStr = c.costos_produccion
            ? `$${c.costos_produccion.toLocaleString("es-MX")}`
            : "N/D";

        const asistenciaProj = c.asistencia_proyectada
            ? c.asistencia_proyectada.toLocaleString("es-MX")
            : "—";

        const asistenciaReal = c.asistencia_real
            ? c.asistencia_real.toLocaleString("es-MX")
            : "—";

        const item = document.createElement("div");
        item.className = "gig-item fade-in";
        item.innerHTML = `
      <div class="d-flex justify-content-between align-items-start flex-wrap">
        <div>
          <div class="gig-title">
            ${c.nombre_evento || "Evento"} @ ${c.venue || "Venue"}
          </div>
          <div class="text-muted" style="font-size:.9rem;">
            ${c.ciudad || "Ciudad"}, ${c.pais || ""} • ${fechaStr}
          </div>
          <div style="font-size:.85rem;" class="mt-1">
            ${statusBadge}
          </div>
        </div>
        <div class="text-end" style="min-width:150px; font-size:.85rem;">
          <div><b>Taquilla:</b> ${ingresosStr}</div>
          <div><b>Costos:</b> ${costosStr}</div>
          <div><b>Asist. Proy:</b> ${asistenciaProj}</div>
          <div><b>Asist. Real:</b> ${asistenciaReal}</div>
        </div>
      </div>
    `;
        listaConciertos.appendChild(item);
    });
}

// Modo oscuro

function aplicarTemaInicial() {
    const temaGuardado = localStorage.getItem("temaPulsePass");
    const rootHtml = document.documentElement;

    if (temaGuardado === "dark") {
        rootHtml.setAttribute("data-bs-theme", "dark");
        modoOscuroToggle.checked = true;
    } else {
        rootHtml.setAttribute("data-bs-theme", "light");
        modoOscuroToggle.checked = false;
    }
}

modoOscuroToggle.addEventListener("change", () => {
    const rootHtml = document.documentElement;
    if (modoOscuroToggle.checked) {
        rootHtml.setAttribute("data-bs-theme", "dark");
        localStorage.setItem("temaPulsePass", "dark");
    } else {
        rootHtml.setAttribute("data-bs-theme", "light");
        localStorage.setItem("temaPulsePass", "light");
    }
});


// Inicialización

document.addEventListener("DOMContentLoaded", async () => {
    aplicarTemaInicial();
    await cargarArtistas(); // llena el dropdown
});
