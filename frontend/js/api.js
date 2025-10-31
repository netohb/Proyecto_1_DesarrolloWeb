const URL_ARTISTAS_BASE = "http://127.0.0.1:8000/api/artistas";
const URL_STATS = "http://127.0.0.1:8000/api/estadisticas/";

// REFERENCIAS DEL DOM 
const selectArtista = document.getElementById("selectArtista");
const infoArtista = document.getElementById("infoArtista");
const chartPopularidad = document.getElementById("chartPopularidad");
const chartRentabilidad = document.getElementById("chartRentabilidad");

// --- MODO (Claro/Oscuro) ---
const root = document.documentElement;
const themeToggle = document.getElementById('modoOscuro');

function applyTheme(theme) {
    root.setAttribute('data-bs-theme', theme);
    localStorage.setItem('pp-theme', theme);

    if (window.Chart) {
        Chart.defaults.color = (theme === 'dark') ? '#eaeaea' : '#212529';
        Chart.defaults.borderColor = (theme === 'dark') ? '#444' : '#e5e7eb';
    }

    if (typeof Chart !== 'undefined' && chart1 instanceof Chart) chart1.update();
    if (typeof Chart !== 'undefined' && chart2 instanceof Chart) chart2.update();

}

// --- SWITCH ---
function initTheme() {
    const saved = localStorage.getItem('pp-theme') || 'light';
    applyTheme(saved);

    if (themeToggle) {
        themeToggle.checked = (saved === 'dark');
        themeToggle.addEventListener('change', () => {
            applyTheme(themeToggle.checked ? 'dark' : 'light');
        });
    }
}


let chart1, chart2;
window.artistasData = []; // Arreglo global para guardar todos los artistas

// CARGAR TODOS LOS ARTISTAS CON PAGINACIÓN

async function cargarArtistas() {
    let allArtists = [];
    let currentPage = 1;
    let hasNext = true;

    try {
        // Bucle para recorrer todas las páginas
        while (hasNext) {
            const response = await fetch(`${URL_ARTISTAS_BASE}?page=${currentPage}&limit=20`);
            const data = await response.json();

            if (data.success && Array.isArray(data.data)) {
                allArtists = allArtists.concat(data.data);
            }

            hasNext = data.pagination?.has_next || false;
            currentPage++;
        }

        // Guarda todos los artistas globalmente
        window.artistasData = allArtists;

        // Llenar el dropdown
        selectArtista.innerHTML = `
      <option selected disabled>Selecciona un artista</option>
      ${allArtists.map(a => `<option value="${a.nombre}">${a.nombre}</option>`).join("")}
    `;

        console.log(`Se cargaron ${allArtists.length} artistas.`);
    } catch (error) {
        console.error("Error al cargar artistas:", error);
        selectArtista.innerHTML = `<option>Error al cargar artistas</option>`;
    }
}

// MOSTRAR INFORMACIÓN DEL ARTISTA SELECCIONADO

selectArtista.addEventListener("change", () => {
    const nombre = selectArtista.value;
    const artista = window.artistasData.find(a => a.nombre === nombre);

    if (artista) {
        infoArtista.innerHTML = `
      <div class="card shadow-sm border-0">
        <div class="row g-0">
          <div class="col-md-4">
            <img src="${artista.imagen_url}" class="img-fluid rounded-start" alt="${artista.nombre}">
          </div>
          <div class="col-md-8">
            <div class="card-body">
              <h5 class="card-title">${artista.nombre}</h5>
              <p class="card-text"><b>Género:</b> ${artista.genero}</p>
              <p class="card-text"><b>País:</b> ${artista.pais}</p>
              <p class="card-text">${artista.biografia}</p>
              <p class="card-text"><b>Popularidad:</b> ${artista.popularidad}</p>
            </div>
          </div>
        </div>
      </div>
    `;
    }
});


// OBTENER Y GRAFICAR ESTADÍSTICAS GLOBALES

async function cargarEstadisticas() {
    try {
        const res = await fetch(URL_STATS);
        const json = await res.json();

        if (!json.success || !json.data) throw new Error("Error al obtener estadísticas");

        const data = json.data;

        // Gráfica 1: Popularidad de los artistas 
        const artistasTop = data.grafica_top_artistas;
        const nombres = artistasTop.map(a => a.nombre);
        const popularidades = artistasTop.map(a => a.popularidad);

        if (chart1) chart1.destroy();
        const uiColor = getComputedStyle(document.body).color;

        chart1 = new Chart(chartPopularidad, {
            type: "bar",
            data: {
                labels: nombres,
                datasets: [{
                    label: "Nivel de popularidad",
                    data: popularidades,
                    backgroundColor: "rgba(227, 0, 82, 0.5)",
                    borderColor: "#e30052",
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "Puntaje de popularidad",
                            font: { size: 14, weight: "bold" }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: "Artistas",
                            font: { size: 14, weight: "bold" }
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: "🎤 Popularidad de los Artistas Top",
                        color: uiColor,
                        font: { size: 18, weight: "bold" },
                        padding: { top: 10, bottom: 20 }
                    },
                    legend: { display: false }
                }
            }
        });

        // Gráfica 2: Rentabilidad por ciudad
        const rentabilidad = data.grafica_rentabilidad_ciudad;
        const ciudades = rentabilidad.map(c => c.ciudad);
        const ganancias = rentabilidad.map(c => c.ganancia_neta_ciudad);

        if (chart2) chart2.destroy();
        chart2 = new Chart(chartRentabilidad, {
            type: "pie",
            data: {
                labels: ciudades,
                datasets: [{
                    label: "Ganancia Neta ($)",
                    data: ganancias,
                    backgroundColor: [
                        "#6f00ff",
                        "#e30052",
                        "#00bcd4",
                        "#ffc107",
                        "#4caf50"
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: "💰 Rentabilidad Neta por Ciudad",
                        color: uiColor,
                        font: { size: 18, weight: "bold" },
                        padding: { top: 10, bottom: 20 }
                    },
                    legend: {
                        position: "bottom",
                        labels: {
                            font: { size: 13 }
                        }
                    }
                }
            }
        });

        console.log("Estadísticas cargadas correctamente");
    } catch (error) {
        console.error("Error al cargar estadísticas:", error);
    }
}


// INICIALIZAR TODO AL CARGAR LA PÁGINA

document.addEventListener("DOMContentLoaded", async () => {
    initTheme();
    await cargarArtistas();
    await cargarEstadisticas();
});
