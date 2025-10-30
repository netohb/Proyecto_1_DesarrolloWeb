const LS_THEME_KEY = 'pp-theme';
const LS_FORM_KEY  = 'pp-register-form';
const LS_QUEUE_KEY = 'pp-pending-queue'; // para guardar envíos si no hay red

const docEl = document.documentElement;
const themeToggleBtn = document.getElementById('themeToggle');

function applyTheme(theme) {
  docEl.setAttribute('data-bs-theme', theme);
  try { localStorage.setItem(LS_THEME_KEY, theme); } catch { /* ignore */ }
  if (themeToggleBtn) themeToggleBtn.textContent = theme === 'dark' ? 'Cambiar a claro' : 'Cambiar a oscuro';
}

(function initTheme(){
  const saved = (typeof localStorage !== 'undefined') ? localStorage.getItem(LS_THEME_KEY) : null;
  applyTheme(saved === 'light' ? 'light' : 'dark'); // default: dark
})();
themeToggleBtn?.addEventListener('click', () => {
  const current = docEl.getAttribute('data-bs-theme') || 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark');
});

// ==================== Form ====================
const form      = document.getElementById('registerForm');
const alertBox  = document.getElementById('alertBox');
const clearBtn  = document.getElementById('clearBtn');
const genresFb  = document.getElementById('genresFeedback');
const netStatus = document.getElementById('netStatus');

// Mostrar/ocultar contraseña
document.getElementById('togglePass')?.addEventListener('click', () => {
  const input = document.getElementById('password');
  if (!input) return;
  input.type = input.type === 'password' ? 'text' : 'password';
  document.getElementById('togglePass').textContent = input.type === 'password' ? 'Mostrar' : 'Ocultar';
});

// Prefill desde localStorage
function prefillFromStorage() {
  try {
    const raw = localStorage.getItem(LS_FORM_KEY);
    if (!raw) return;
    const data = JSON.parse(raw);

    Object.entries(data).forEach(([name, value]) => {
      const el = form?.elements.namedItem(name);
      if (!el) return;

      if (name === 'genres' && Array.isArray(value)) {
        document.querySelectorAll('input[name="genres"]').forEach(cb => {
          cb.checked = value.includes(cb.value);
        });
      } else if (el instanceof RadioNodeList) {
        // no radios aquí
      } else if ('type' in el && el.type === 'checkbox') {
        el.checked = !!value;
      } else if ('value' in el) {
        el.value = value ?? '';
      }
    });
  } catch { /* ignora */ }
}

// Guardar formulario
function serializeForm() {
  const data = {};
  const genres = [];
  Array.from(form.elements).forEach(el => {
    if (!el.name) return;
    if (el.name === 'genres') {
      if (el.checked) genres.push(el.value);
      return;
    }
    if (el.type === 'checkbox') data[el.name] = el.checked;
    else data[el.name] = el.value;
  });
  if (genres.length) data.genres = genres;
  return data;
}

function saveFormToStorage() {
  try {
    const data = serializeForm();
    localStorage.setItem(LS_FORM_KEY, JSON.stringify(data));
  } catch { /* ignora */ }
}

function showAlert(kind, msg) {
  if (!alertBox) return;
  alertBox.className = `alert alert-${kind}`;
  alertBox.textContent = msg;
  alertBox.classList.remove('d-none');
  // Ocultar después de 2s si es success/info
  if (kind === 'success' || kind === 'info') {
    setTimeout(() => alertBox.classList.add('d-none'), 2000);
  }
}

// Validación de géneros (al menos 1)
function validateGenres() {
  const any = document.querySelectorAll('input[name="genres"]:checked').length > 0;
  if (any) genresFb?.classList.remove('d-block');
  else genresFb?.classList.add('d-block');
  return any;
}

// Eventos del formulario
form?.addEventListener('input', saveFormToStorage);        // autoguardado en cada cambio
window.addEventListener('beforeunload', saveFormToStorage); // guarda al salir
document.getElementById('genresGroup')?.addEventListener('change', validateGenres);

clearBtn?.addEventListener('click', () => {
  try { localStorage.removeItem(LS_FORM_KEY); } catch {}
  form?.reset();
  form?.classList.remove('was-validated');
  genresFb?.classList.remove('d-block');
  showAlert('info', 'Formulario limpio.');
});

// ==================== Envío (con stub de API y manejo 2xx/4xx/5xx) ====================
async function submitToAPI(payload) {

  const url = '/api/registro'; //API---------------------------------------------------

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    // Casos 2xx (exito)
    if (res.ok) {
      const json = await res.json().catch(() => ({}));
      return { ok: true, data: json, status: res.status };
    }

    // Casos 4xx / 5xx (error)
    const errorText = await res.text().catch(() => '');
    return { ok: false, status: res.status, message: errorText || 'Error en la API' };

  } catch (err) {
    // Error de red (offline / CORS / timeout)
    return { ok: false, status: 0, message: 'Sin conexión con el servidor' };
  }
}

function queuePending(payload) {
  try {
    const raw = localStorage.getItem(LS_QUEUE_KEY);
    const arr = raw ? JSON.parse(raw) : [];
    arr.push({ payload, ts: Date.now() });
    localStorage.setItem(LS_QUEUE_KEY, JSON.stringify(arr));
  } catch { /* ignora */ }
}

// Bootstrap validation + envío
form?.addEventListener('submit', async (e) => {
  e.preventDefault();
  form.classList.add('was-validated');

  // Validación nativa + géneros
  if (!form.checkValidity() || !validateGenres()) return;

  const data = serializeForm();

  // Simulación: si no hay backend aún, guardamos local y mostramos éxito.
  // Quita este bloque cuando conectes tu API real.
  const USE_STUB = false; // pon true si quieres forzar stub sin llamar al servidor
  if (USE_STUB) {
    saveFormToStorage();
    showAlert('success', 'Registrado (modo local).');
    return;
  }

  // Llamada real (cuando exista tu endpoint)
  const result = await submitToAPI(data);
  if (result.ok) {
    saveFormToStorage();
    showAlert('success', 'Registro exitoso.');
  } else {
    if (result.status === 0) {
      // sin red: lo ponemos en cola local para reintento
      queuePending(data);
      showAlert('warning', 'Sin conexión. Se guardó localmente para reintentar.');
    } else if (String(result.status).startsWith('4')) {
      showAlert('danger', `Error del cliente (${result.status}). Revisa tus datos.`);
    } else {
      showAlert('danger', `Error del servidor (${result.status}). Intenta más tarde.`);
    }
  }
});

// ==================== Eventos "nuevos" para tu rúbrica ====================
// 1) Cambios de conexión (online/offline)
function updateNetStatus() {
  if (!netStatus) return;
  const online = navigator.onLine;
  netStatus.textContent = online ? 'Conectado' : 'Sin conexión';
}
window.addEventListener('online',  updateNetStatus);
window.addEventListener('offline', updateNetStatus);

// 2) Visibilidad de la pestaña (autosave cuando vuelves)
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') saveFormToStorage();
});

// Inicializaciones finales
prefillFromStorage();
updateNetStatus();
validateGenres();
