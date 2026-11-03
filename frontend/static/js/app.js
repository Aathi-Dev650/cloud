(() => {
  const root = document.getElementById('root');
  const esc = value => String(value).replace(/[&<>"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
  const config = window.CROPCURE_AUTH0 || {};
  root.innerHTML = `<main class="heritage-auth"><section class="auth-legacy"><div class="kolam-mark">🌱</div><p class="tamil-script">CROPCURE AI · FARMER CARE</p><h1>Rooted in Tamil soil.</h1><p>Identify crop diseases, save your field observations, and find locally relevant guidance.</p><div class="nammalvar-note"><span>🌾</span><p>In the spirit of G. Nammalvar: care for soil, seed, water, and every living thing.</p></div></section><section class="auth-panel"><div class="auth-topline">CROPCURE <span>FARMER JOURNAL</span></div><h2>Vanakkam, farmer</h2><p>Sign in to continue caring for your crop.</p><div id="auth-message" class="notice"></div><button id="auth-login" class="primary" type="button">Sign in</button><button id="auth-signup" class="primary" type="button">Create an account</button><p class="auth-switch">Secure sign in powered by Auth0.</p></section></main>`;
  const message = document.getElementById('auth-message');
  if (!config.domain || !config.clientId || !config.audience) {
    message.textContent = 'Add your Auth0 domain, client ID, and API audience to .env, then restart CropCure.';
    message.hidden = false;
  }
  window.cropcureAuth?.then(async client => {
    if (!client) {
      if (!message.textContent) message.textContent = 'Auth0 could not start. Check your Auth0 settings and reload.';
      message.hidden = false;
      return;
    }
    if (await client.isAuthenticated()) window.location.replace('/home.html');
    document.getElementById('auth-login').onclick = () => client.loginWithRedirect();
    document.getElementById('auth-signup').onclick = () => client.loginWithRedirect({authorizationParams: {screen_hint: 'signup'}});
  });
})();
