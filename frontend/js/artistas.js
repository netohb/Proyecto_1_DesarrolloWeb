const API_URL = "http://127.0.0.1:8000/api/artistas";
const contenedor = document.getElementById("contenedorArtistas");

// Cargar todos los artistas con paginación automática
async function cargarArtistas() {
    let artistas = [];
    let page = 1;
    let hasNext = true;

    try {
        while (hasNext) {
            const res = await fetch(`${API_URL}?page=${page}&limit=20`);
            const json = await res.json();

            if (json.success && Array.isArray(json.data)) {
                artistas = artistas.concat(json.data);
            }

            hasNext = json.pagination?.has_next || false;
            page++;
        }

        mostrarArtistas(artistas);
    } catch (error) {
        console.error("Error al obtener artistas:", error);
    }
}

// Mostrar artistas en tarjetas con animación
function mostrarArtistas(lista) {
    contenedor.innerHTML = "";

    if (lista.length === 0) {
        contenedor.innerHTML = `<p class="text-center text-muted">No hay artistas disponibles.</p>`;
        return;
    }

    lista.forEach((artista, index) => {
        const col = document.createElement("div");
        col.className = "col-md-4 col-lg-3 d-flex justify-content-center";

        const card = document.createElement("div");
        card.className = "card text-center h-100";
        card.innerHTML = `
      <img src="${artista.imagen_url}" class="card-img-top" alt="${artista.nombre}">
      <div class="card-body">
        <h5 class="card-title">${artista.nombre}</h5>
        <p class="card-text"><b>País:</b> ${artista.pais}</p>
        <p class="card-text"><b>Popularidad:</b> ${artista.popularidad}</p>
        <p class="card-text">${artista.biografia}</p>
      </div>
    `;

        // animación suave
        setTimeout(() => card.classList.add("show"), index * 80);

        col.appendChild(card);
        contenedor.appendChild(col);
    });
}

// Inicializar
document.addEventListener("DOMContentLoaded", cargarArtistas);
