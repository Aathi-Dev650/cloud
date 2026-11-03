(() => {
  const config = window.CROPCURE_AUTH0 || {};
  window.cropcureAuth = (async () => {
    if (!config.domain || !config.clientId || !config.audience || !window.auth0?.createAuth0Client) return null;
    const client = await window.auth0.createAuth0Client({
      domain: config.domain,
      clientId: config.clientId,
      cacheLocation: 'memory',
      authorizationParams: { redirect_uri: config.redirectUri || window.location.origin + '/', audience: config.audience },
    });
    if (new URLSearchParams(window.location.search).has('code') && new URLSearchParams(window.location.search).has('state')) {
      await client.handleRedirectCallback();
      window.history.replaceState({}, document.title, window.location.pathname);
    }
    if (await client.isAuthenticated()) {
      const profile = await client.getUser();
      const token = await client.getTokenSilently();
      await fetch('/api/disease/auth/me/', {
        method: 'POST',
        headers: {'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json'},
        body: JSON.stringify({full_name: profile?.name || '', email: profile?.email || ''}),
      });
    }
    return client;
  })().catch(error => {
    console.error('Auth0 initialization failed', error);
    return null;
  });
})();
