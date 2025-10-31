const API_BASE = "http://127.0.0.1:8000";
const LS_THEME_KEY = 'pp-theme';
const LS_REMEMBER  = 'pp-remember-email';
const LS_TOKEN     = 'pp-auth-token'; // (solo dev)

// ===== Tema persistente =====
const docEl = document.documentElement;
const btnTheme = document.getElementById('themeToggle');
function applyTheme(t){
  docEl.setAttribute('data-bs-theme', t);
  try{ localStorage.setItem(LS_THEME_KEY, t); }catch{}
  btnTheme.textContent = t==='dark' ? 'Cambiar a claro' : 'Cambiar a oscuro';
}
(function initTheme(){
  const saved = (typeof localStorage!=='undefined') ? localStorage.getItem(LS_THEME_KEY) : null;
  applyTheme(saved === 'light' ? 'light' : 'dark');
})();
btnTheme?.addEventListener('click', ()=>{
  const curr = docEl.getAttribute('data-bs-theme') || 'dark';
  applyTheme(curr==='dark' ? 'light' : 'dark');
});

// ===== Util =====
const alertBox = document.getElementById('alertBox');
function showAlert(type,msg){
  alertBox.className = `alert alert-${type}`;
  alertBox.textContent = msg;
  alertBox.classList.remove('d-none');
  if(type!=='danger') setTimeout(()=>alertBox.classList.add('d-none'), 2000);
}

// ===== Form =====
const form = document.getElementById('loginForm');
const emailEl = document.getElementById('email');
const passEl  = document.getElementById('password');
const rememberEl = document.getElementById('remember');

document.getElementById('togglePass')?.addEventListener('click', ()=>{
  passEl.type = passEl.type === 'password' ? 'text' : 'password';
  document.getElementById('togglePass').textContent = passEl.type === 'password' ? 'Mostrar' : 'Ocultar';
});

// Prefill remember
(function loadRemember(){
  try{
    const savedEmail = localStorage.getItem(LS_REMEMBER);
    if(savedEmail){ emailEl.value = savedEmail; rememberEl.checked = true; }
  }catch{}
})();

// Fake recover link
document.getElementById('recoverLink')?.addEventListener('click', (e)=>{
  e.preventDefault();
  showAlert('info','Función de recuperación pendiente.');
});

// ===== API =====
async function login(email, password){
  const url = `${API_BASE}/api/login`; // ajusta al endpoint real
  try{
    const res  = await fetch(url, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ email, password })
    });
    const text = await res.text();
    let data = {};
    try{ data = text ? JSON.parse(text) : {}; }catch{}

    if(res.ok){
      return { ok:true, data, status:res.status };
    }else{
      const msg = data.detail || data.message || text || 'Error en la API';
      return { ok:false, status:res.status, message: msg };
    }
  }catch{
    return { ok:false, status:0, message:'Sin conexión con el servidor' };
  }
}

// ===== Submit =====
form?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  form.classList.add('was-validated');
  if(!form.checkValidity()) return;

  const email = emailEl.value.trim();
  const password = passEl.value;

  // Remember email
  try{
    if(rememberEl.checked) localStorage.setItem(LS_REMEMBER, email);
    else localStorage.removeItem(LS_REMEMBER);
  }catch{}

  const result = await login(email, password);
  if(result.ok){
    // Guarda token si viene (solo dev). Ajusta el nombre del campo (token, access_token, etc.)
    const token = result.data.token || result.data.access_token || null;
    if(token){
      try{ localStorage.setItem(LS_TOKEN, token); }catch{}
    }
    showAlert('success','Inicio de sesión exitoso.');
    // Redirige a tu dashboard cuando esté listo:
    // window.location.href = './dashboard.html';
  }else{
    if(result.status===0)      showAlert('warning','Sin conexión con el servidor.');
    else if(String(result.status).startsWith('4')) showAlert('danger','Credenciales inválidas.');
    else                      showAlert('danger','Error del servidor. Intenta más tarde.');
  }
});