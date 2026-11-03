(() => {
  const api = '/api/disease/';
  const cookie = name => document.cookie.split('; ').find(value => value.startsWith(`${name}=`))?.split('=')[1] || '';
  const request = async (path, options = {}) => {
    const headers = options.body instanceof FormData ? {} : {'Content-Type': 'application/json'};
    if (options.method === 'POST') headers['X-CSRFToken'] = cookie('csrftoken');
    const client = await window.cropcureAuth;
    if (!client) throw new Error('Auth0 is not configured. Check your local .env settings.');
    const token = await client.getTokenSilently();
    headers.Authorization = `Bearer ${token}`;
    const response = await fetch(api + path, {credentials: 'same-origin', ...options, headers: {...headers, ...options.headers}});
    const data = response.status === 204 ? null : await response.json();
    if (!response.ok) { const error = new Error(data?.detail || 'Something went wrong.'); error.status = response.status; throw error; }
    return data;
  };
  const list = items => `<ul>${(items || []).map(item => `<li>${item}</li>`).join('')}</ul>`;
  const redirectToLogin = () => { window.location.replace('/'); };
  const copy = {
    English: {home:'Home', detection:'Detection', results:'Results', history:'History', profile:'Profile', earth:'Nilam · Earth', water:'Neer · Water', fire:'Aggini · Fire', air:'Kaatru · Air', ether:'Aagayam · Ether', homeTitle:'The field knows first.', homeLead:'Observe your crop closely. CropCure helps turn that wisdom into timely action.', detectionTitle:'Listen to every leaf.', detectionLead:'A calm space to examine the story your crop is telling.', resultsTitle:'Turn insight into care.', resultsLead:'Practical next steps, rooted in local farming wisdom.', historyTitle:'A breeze through your field journal.', historyLead:'Every observation is a step toward a healthier season.', profileTitle:'Your place in the field.', profileLead:'The farmer, the soil, and the knowledge that connects them.', symptoms:'Symptoms', solution:'Recommended solution', prevention:'Preventive measures', disease:'Disease detected', noGuidance:'Guidance has not yet been configured for this diagnosis.', retakeTitle:'Please retake the photo', retakeText:'We could not identify this leaf with enough confidence. Photograph one leaf in good daylight, keep it in focus, and avoid hands or other leaves in the frame.', noAssessment:'No assessment selected', analyzePrompt:'Analyze a plant to see recommendations.', total:'Total analyses', thisMonth:'This month', healthy:'Healthy checks', date:'Date', crop:'Crop', status:'Status', action:'Action', view:'View', noRecords:'No analyses yet.', uploading:'Please upload a plant image.', detecting:'🔬 Reading the leaf…', analyze:'🔬 Analyze Plant', farmer:'CropCure AI Farmer', activeFarmer:'🌱 Active Farmer', account:'📋 Account Information', username:'Username', email:'Email address', mobile:'Mobile number', district:'District', state:'State', preferredLanguage:'Preferred language', memberSince:'Member since', accountStatus:'Account status', active:'🟢 Active', notProvided:'Not provided', about:'🌱 About CropCure AI', aboutText:'CropCure AI helps farmers identify plant diseases and provides locally relevant management guidance.', editProfile:'✏️ Edit profile', logout:'🚪 Logout', updateDetails:'Update your farmer details', fullName:'Full name', language:'Language', save:'Save details'},
    'தமிழ்': {home:'முகப்பு', detection:'கண்டறிதல்', results:'முடிவுகள்', history:'வரலாறு', profile:'சுயவிவரம்', earth:'நிலம் · மண்', water:'நீர் · வாழ்வு', fire:'அக்கினி · மாற்றம்', air:'காற்று · சுவாசம்', ether:'ஆகாயம் · இணைப்பு', homeTitle:'வயல் முதலில் பேசும்.', homeLead:'பயிரை கவனமாகப் பாருங்கள். சரியான நேரத்தில் செயல்பட CropCure உதவும்.', detectionTitle:'ஒவ்வோர் இலையையும் கேளுங்கள்.', detectionLead:'உங்கள் பயிரின் கதையை அறிய அமைதியான இடம்.', resultsTitle:'அறிவை பராமரிப்பாக மாற்றுங்கள்.', resultsLead:'உள்ளூர் வேளாண் அறிவில் வேரூன்றிய நடைமுறை வழிகாட்டல்.', historyTitle:'உங்கள் வயல் பதிவேட்டில் ஒரு தென்றல்.', historyLead:'ஒவ்வொரு கவனிப்பும் ஆரோக்கியமான பருவத்திற்கான ஒரு படி.', profileTitle:'வயலில் உங்கள் இடம்.', profileLead:'விவசாயி, மண், அவற்றை இணைக்கும் அறிவு.', symptoms:'அறிகுறிகள்', solution:'பரிந்துரைக்கப்பட்ட தீர்வு', prevention:'தடுப்பு நடவடிக்கைகள்', disease:'கண்டறியப்பட்ட நோய்', noGuidance:'இந்த நோயறிதலுக்கான வழிகாட்டல் இன்னும் சேர்க்கப்படவில்லை.', noAssessment:'மதிப்பீடு தேர்ந்தெடுக்கப்படவில்லை', analyzePrompt:'வழிகாட்டலைப் பார்க்க ஒரு பயிரை ஆய்வு செய்யுங்கள்.', total:'மொத்த ஆய்வுகள்', thisMonth:'இந்த மாதம்', healthy:'ஆரோக்கியமான ஆய்வுகள்', date:'தேதி', crop:'பயிர்', status:'நிலை', action:'செயல்', view:'பார்க்க', noRecords:'இன்னும் ஆய்வுகள் இல்லை.', uploading:'தயவுசெய்து பயிர் படத்தைப் பதிவேற்றவும்.', detecting:'🔬 இலையைப் படிக்கிறது…', analyze:'🔬 பயிரை ஆய்வு செய்', farmer:'CropCure AI விவசாயி', activeFarmer:'🌱 செயலில் உள்ள விவசாயி', account:'📋 கணக்கு தகவல்', username:'பயனர்பெயர்', email:'மின்னஞ்சல் முகவரி', mobile:'கைபேசி எண்', district:'மாவட்டம்', state:'மாநிலம்', preferredLanguage:'விருப்ப மொழி', memberSince:'உறுப்பினரான நாள்', accountStatus:'கணக்கு நிலை', active:'🟢 செயலில் உள்ளது', notProvided:'வழங்கப்படவில்லை', about:'🌱 CropCure AI பற்றி', aboutText:'CropCure AI பயிர் நோய்களைக் கண்டறிந்து உள்ளூர் சூழலுக்கு ஏற்ற பராமரிப்பு வழிகாட்டலை வழங்குகிறது.', editProfile:'✏️ சுயவிவரத்தைத் திருத்து', logout:'🚪 வெளியேறு', updateDetails:'உங்கள் விவசாயி விவரங்களைப் புதுப்பிக்கவும்', fullName:'முழுப் பெயர்', language:'மொழி', save:'விவரங்களைச் சேமி'},
    'हिन्दी': {home:'होम', detection:'पहचान', results:'परिणाम', history:'इतिहास', profile:'प्रोफ़ाइल', earth:'नीलम · धरती', water:'नीर · जल', fire:'अग्नि · परिवर्तन', air:'कात्रु · वायु', ether:'आगायम · आकाश', homeTitle:'खेत पहले जानता है।', homeLead:'अपनी फसल को ध्यान से देखें। CropCure सही समय पर कदम उठाने में मदद करता है।', detectionTitle:'हर पत्ते को सुनिए।', detectionLead:'अपनी फसल की कहानी को समझने का शांत स्थान।', resultsTitle:'जानकारी को देखभाल में बदलें।', resultsLead:'स्थानीय कृषि ज्ञान पर आधारित व्यावहारिक अगले कदम।', historyTitle:'आपकी खेत डायरी में एक हवा।', historyLead:'हर निरीक्षण स्वस्थ मौसम की ओर एक कदम है।', profileTitle:'खेत में आपका स्थान।', profileLead:'किसान, मिट्टी और उन्हें जोड़ने वाला ज्ञान।', symptoms:'लक्षण', solution:'सुझाया गया समाधान', prevention:'रोकथाम के उपाय', disease:'पहचाना गया रोग', noGuidance:'इस निदान के लिए मार्गदर्शन अभी उपलब्ध नहीं है।', noAssessment:'कोई आकलन चयनित नहीं है', analyzePrompt:'मार्गदर्शन देखने के लिए फसल का विश्लेषण करें।', total:'कुल विश्लेषण', thisMonth:'इस महीने', healthy:'स्वस्थ जांच', date:'तारीख', crop:'फसल', status:'स्थिति', action:'कार्य', view:'देखें', noRecords:'अभी कोई विश्लेषण नहीं है।', uploading:'कृपया फसल की तस्वीर अपलोड करें।', detecting:'🔬 पत्ते को पढ़ रहा है…', analyze:'🔬 फसल का विश्लेषण करें', farmer:'CropCure AI किसान', activeFarmer:'🌱 सक्रिय किसान', account:'📋 खाता जानकारी', username:'उपयोगकर्ता नाम', email:'ईमेल पता', mobile:'मोबाइल नंबर', district:'जिला', state:'राज्य', preferredLanguage:'पसंदीदा भाषा', memberSince:'सदस्यता तिथि', accountStatus:'खाता स्थिति', active:'🟢 सक्रिय', notProvided:'उपलब्ध नहीं', about:'🌱 CropCure AI के बारे में', aboutText:'CropCure AI किसानों को पौधों के रोग पहचानने और स्थानीय परिस्थितियों के अनुकूल देखभाल मार्गदर्शन देने में मदद करता है।', editProfile:'✏️ प्रोफ़ाइल संपादित करें', logout:'🚪 साइन आउट', updateDetails:'अपने किसान विवरण अपडेट करें', fullName:'पूरा नाम', language:'भाषा', save:'विवरण सहेजें'}
  };
  const language = () => sessionStorage.getItem('cropcureLanguage') || 'English';
  const t = key => (copy[language()] || copy.English)[key] || copy.English[key] || key;
  const staticCopy = {
    English: {},
    'தமிழ்': {
      'Smart Farming With AI Technology':'செயற்கை நுண்ணறிவுடன் சிறந்த விவசாயம்', 'Identify plant diseases instantly using Artificial Intelligence and get natural organic remedies to protect your crops.':'செயற்கை நுண்ணறிவு மூலம் பயிர் நோய்களை உடனடியாகக் கண்டறிந்து இயற்கைத் தீர்வுகளைப் பெறுங்கள்.', 'Start Plant Analysis':'பயிர் ஆய்வைத் தொடங்கு', 'Healthy Plants Create A Healthy Future':'ஆரோக்கியமான பயிர்கள் ஆரோக்கியமான எதிர்காலத்தை உருவாக்கும்', 'Empowering farmers with technology, knowledge and sustainable solutions.':'தொழில்நுட்பம், அறிவு, நிலையான தீர்வுகளால் விவசாயிகளுக்கு வலிமை அளிக்கிறோம்.', 'Why Choose CropCure AI?':'ஏன் CropCure AI?', 'AI Disease Detection':'செயற்கை நுண்ணறிவு நோய் கண்டறிதல்', 'Upload plant images and detect diseases accurately.':'பயிர் படங்களைப் பதிவேற்றி நோய்களைத் துல்லியமாகக் கண்டறியுங்கள்.', 'Organic Remedies':'இயற்கைத் தீர்வுகள்', 'Get natural solutions to protect crops.':'பயிர்களைப் பாதுகாக்க இயற்கைத் தீர்வுகளைப் பெறுங்கள்.', 'Smart Farming':'சிறந்த விவசாயம்', 'Use weather and soil information for better decisions.':'சிறந்த முடிவுகளுக்கு வானிலை மற்றும் மண் தகவல்களைப் பயன்படுத்துங்கள்.', 'How CropCure AI Works':'CropCure AI எப்படி செயல்படுகிறது?', 'Upload':'பதிவேற்று', 'Upload diseased plant image':'நோயுற்ற பயிர் படத்தைப் பதிவேற்று', 'Analyze':'ஆய்வு செய்', 'AI identifies the disease':'AI நோயைக் கண்டறியும்', 'Solution':'தீர்வு', 'Get organic treatment':'இயற்கை சிகிச்சையைப் பெறுங்கள்', 'Analyze Your Plant':'உங்கள் பயிரை ஆய்வு செய்யுங்கள்', 'Upload a clear photo of your plant to identify possible diseases and get organic treatment recommendations.':'சாத்தியமான நோய்களை அறியவும் இயற்கைச் சிகிச்சை பரிந்துரைகளைப் பெறவும் தெளிவான பயிர் படத்தைப் பதிவேற்றுங்கள்.', 'Upload your plant image':'உங்கள் பயிர் படத்தைப் பதிவேற்றுங்கள்', 'Analysis History':'ஆய்வு வரலாறு'
    },
    'हिन्दी': {
      'Smart Farming With AI Technology':'AI तकनीक के साथ स्मार्ट खेती', 'Identify plant diseases instantly using Artificial Intelligence and get natural organic remedies to protect your crops.':'कृत्रिम बुद्धिमत्ता से पौधों के रोग पहचानें और प्राकृतिक उपचार पाएं।', 'Start Plant Analysis':'फसल विश्लेषण शुरू करें', 'Healthy Plants Create A Healthy Future':'स्वस्थ पौधे स्वस्थ भविष्य बनाते हैं', 'Empowering farmers with technology, knowledge and sustainable solutions.':'तकनीक, ज्ञान और टिकाऊ समाधानों से किसानों को सशक्त बनाना।', 'Why Choose CropCure AI?':'CropCure AI क्यों चुनें?', 'AI Disease Detection':'AI रोग पहचान', 'Upload plant images and detect diseases accurately.':'पौधों की तस्वीरें अपलोड करें और रोगों की सटीक पहचान करें।', 'Organic Remedies':'प्राकृतिक उपचार', 'Get natural solutions to protect crops.':'फसलों की रक्षा के लिए प्राकृतिक समाधान पाएं।', 'Smart Farming':'स्मार्ट खेती', 'Use weather and soil information for better decisions.':'बेहतर निर्णय के लिए मौसम और मिट्टी की जानकारी लें।', 'How CropCure AI Works':'CropCure AI कैसे काम करता है?', 'Upload':'अपलोड', 'Upload diseased plant image':'रोगग्रस्त पौधे की तस्वीर अपलोड करें', 'Analyze':'विश्लेषण', 'AI identifies the disease':'AI रोग पहचानता है', 'Solution':'समाधान', 'Get organic treatment':'प्राकृतिक उपचार पाएं', 'Analyze Your Plant':'अपनी फसल का विश्लेषण करें', 'Upload a clear photo of your plant to identify possible diseases and get organic treatment recommendations.':'संभावित रोगों की पहचान और प्राकृतिक उपचार सुझावों के लिए अपनी फसल की स्पष्ट तस्वीर अपलोड करें।', 'Upload your plant image':'अपनी फसल की तस्वीर अपलोड करें', 'Analysis History':'विश्लेषण इतिहास'
    }
  };
  const localizeStatic = () => {
    const map = staticCopy[language()] || {};
    if (!Object.keys(map).length) return;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const nodes = []; let node;
    while ((node = walker.nextNode())) nodes.push(node);
    nodes.forEach(textNode => { const key = textNode.nodeValue.replace(/\s+/g, ' ').trim(); if (map[key]) textNode.nodeValue = textNode.nodeValue.replace(/\S[\s\S]*\S/, map[key]); });
    document.documentElement.lang = language() === 'தமிழ்' ? 'ta' : language() === 'हिन्दी' ? 'hi' : 'en';
  };
  localizeStatic();

  async function requireUser() {
    const client = await window.cropcureAuth;
    if (!client || !(await client.isAuthenticated())) { redirectToLogin(); throw new Error('Please sign in first.'); }
    try { return await request('auth/me/'); }
    catch (error) {
      if (error.status === 401 || error.status === 403) redirectToLogin();
      else alert(error.message);
      throw error;
    }
  }

  function showResult(result) {
    const card = document.querySelector('.card');
    if (!card) return;
    if (result.needs_retake) {
      card.innerHTML = `<h2>📷 ${t('retakeTitle')}</h2><p>${t('retakeText')}</p>`;
      return;
    }
    card.innerHTML = `${result.image_url ? `<img src="${result.image_url}" alt="Saved crop leaf photo" style="max-width:100%;border-radius:12px;margin-bottom:16px">` : ''}<h2>🌿 ${t('disease')}: ${result.disease}</h2>
      ${result.guidance_available ? `<h3>${t('symptoms')}</h3>${list(result.symptoms)}<h3>${t('solution')}</h3>${list(result.solution)}<h3>${t('prevention')}</h3>${list(result.prevention)}` : `<p>${t('noGuidance')}</p>`}`;
  }

  async function setupDetection() {
    await requireUser();
    document.getElementById('soil')?.closest('.form-group')?.remove();
    document.getElementById('season')?.closest('.form-group')?.remove();
    const input = document.getElementById('imageInput');
    const button = document.querySelector('.analyze-button');
    if (!input || !button) return;
    window.analyzePlant = async () => {
      const image = input.files[0];
      if (!image) return alert(t('uploading'));
      button.disabled = true;
      button.textContent = t('detecting');
      try {
        await fetch('/'); // ensures a CSRF cookie is available on direct page visits
        const body = new FormData(); body.append('image', image);
        const result = await request('create/', {method: 'POST', body});
        sessionStorage.setItem('cropcureLatestResult', JSON.stringify(result));
        window.location.href = '/recommend.html';
      } catch (error) { alert(error.message); }
      finally { button.disabled = false; button.textContent = t('analyze'); }
    };
    button.onclick = event => { event.preventDefault(); window.analyzePlant(); };
  }

  async function setupResults() {
    await requireUser();
    let result = JSON.parse(sessionStorage.getItem('cropcureLatestResult') || 'null');
    if (!result) {
      const history = await request('history/');
      result = history[0];
    }
    if (result) showResult(result);
    else document.querySelector('.card').innerHTML = `<h2>${t('noAssessment')}</h2><p>${t('analyzePrompt')}</p>`;
    window.analyzeAgain = () => { window.location.href = '/detection.html'; };
  }

  async function setupHistory() {
    await requireUser();
    const records = await request('history/');
    const summary = document.querySelectorAll('.summary .card h2');
    if (summary.length >= 3) {
      const month = new Date().getMonth();
      summary[0].previousElementSibling.textContent = t('total'); summary[1].previousElementSibling.textContent = t('thisMonth'); summary[2].previousElementSibling.textContent = t('healthy');
      summary[0].textContent = records.length;
      summary[1].textContent = records.filter(item => new Date(item.created_at).getMonth() === month).length;
      summary[2].textContent = records.filter(item => item.status === 'No Disease Detected').length;
    }
    const table = document.querySelector('table');
    if (!table) return;
    table.querySelector('thead').innerHTML = `<tr><th>${t('date')}</th><th>${t('crop')}</th><th>${t('disease')}</th><th>${t('status')}</th><th>${t('action')}</th></tr>`;
    table.querySelector('tbody').innerHTML = records.length ? records.map((item, index) => `<tr><td>${new Date(item.created_at).toLocaleDateString()}</td><td>${item.crop}</td><td>${item.disease}</td><td>${item.status}</td><td><button class="view-btn" data-index="${index}">${t('view')}</button></td></tr>`).join('') : `<tr><td colspan="5">${t('noRecords')}</td></tr>`;
    table.querySelectorAll('[data-index]').forEach(button => button.onclick = () => { sessionStorage.setItem('cropcureLatestResult', JSON.stringify(records[button.dataset.index])); window.location.href = '/recommend.html'; });
  }

  async function setupProfile() {
    const user = await requireUser();
    const card = document.querySelector('.profile-card');
    if (!card) return;
    const joined = user.joined_at ? new Date(user.joined_at).toLocaleDateString() : t('notProvided');
    card.innerHTML = `<div class="profile-header"><div class="profile-image">👨‍🌾</div><div><h2>${user.name}</h2><p>${t('farmer')}</p><span class="farmer-badge">${t('activeFarmer')}</span></div></div>
      <div class="profile-content"><h3 class="section-title">${t('account')}</h3><div class="details-grid">
      <div class="detail-box"><div class="detail-label">${t('username')}</div><div class="detail-value">${user.username}</div></div>
      <div class="detail-box"><div class="detail-label">${t('email')}</div><div class="detail-value">${user.email || t('notProvided')}</div></div>
      <div class="detail-box"><div class="detail-label">${t('mobile')}</div><div class="detail-value">${user.mobile_number || t('notProvided')}</div></div>
      <div class="detail-box"><div class="detail-label">${t('district')}</div><div class="detail-value">${user.district || t('notProvided')}</div></div>
      <div class="detail-box"><div class="detail-label">${t('state')}</div><div class="detail-value">${user.state || 'Tamil Nadu'}, India</div></div>
      <div class="detail-box"><div class="detail-label">${t('preferredLanguage')}</div><div class="detail-value">${user.language || 'English'}</div></div>
      <div class="detail-box"><div class="detail-label">${t('memberSince')}</div><div class="detail-value">📅 ${joined}</div></div>
      <div class="detail-box"><div class="detail-label">${t('accountStatus')}</div><div class="detail-value">${t('active')}</div></div>
      </div><div class="farm-info"><h3>${t('about')}</h3><p>${t('aboutText')}</p></div><div class="button-container"><button class="edit-btn">${t('editProfile')}</button><button class="logout-btn">${t('logout')}</button></div></div>`;
    const editor = document.createElement('section');
    editor.className = 'profile-editor';
    editor.innerHTML = `<h3>${t('updateDetails')}</h3><form class="form"><label>${t('fullName')}<input name="full_name" value="${user.name}"></label><label>${t('email')}<input name="email" type="email" value="${user.email || ''}"></label><label>${t('mobile')}<input name="mobile_number" value="${user.mobile_number || ''}" inputmode="numeric"></label><label>${t('district')}<input name="district" value="${user.district || ''}"></label><label>${t('state')}<input name="state" value="${user.state || 'Tamil Nadu'}"></label><label>${t('language')}<select name="language"><option>English</option><option>தமிழ்</option><option>हिन्दी</option></select></label><button class="primary">${t('save')}</button></form>`;
    editor.hidden = true;
    card.querySelector('.profile-content').append(editor);
    editor.querySelector('[name="language"]').value = user.language || 'English';
    card.querySelector('.edit-btn').onclick = () => { editor.hidden = !editor.hidden; };
    editor.querySelector('form').onsubmit = async event => { event.preventDefault(); const form = new FormData(event.currentTarget); try { const updated = await request('auth/profile/', {method: 'POST', body: JSON.stringify(Object.fromEntries(form))}); sessionStorage.setItem('cropcureLanguage', updated.language); window.location.reload(); } catch (error) { alert(error.message); } };
    const logout = async () => { const client = await window.cropcureAuth; client.logout({logoutParams: {returnTo: (window.CROPCURE_AUTH0 || {}).logoutUri || window.location.origin + '/'}}); };
    window.logout = logout;
    document.querySelectorAll('.logout-btn').forEach(button => button.onclick = event => { event.preventDefault(); logout(); });
  }

  const page = location.pathname;
  const pageDetails = {
    '/home.html': ['earth', 'homeTitle', 'homeLead'],
    '/detection.html': ['water', 'detectionTitle', 'detectionLead'],
    '/recommend.html': ['fire', 'resultsTitle', 'resultsLead'],
    '/history.html': ['air', 'historyTitle', 'historyLead'],
    '/profile.html': ['ether', 'profileTitle', 'profileLead'],
  };
  const detail = pageDetails[page];
  const elementNames = { '/home.html': 'nilam', '/detection.html': 'neer', '/recommend.html': 'aggini', '/history.html': 'kaatru', '/profile.html': 'aagayam' };
  document.body.dataset.element = elementNames[page] || '';
  const nav = document.querySelector('nav');
  if (detail && nav) {
    const banner = document.createElement('section');
    banner.className = 'cropcure-banner';
    banner.innerHTML = `<div><span class="cropcure-kicker">${t(detail[0])} · CROPCURE AI</span><h1>${t(detail[1])}</h1><p>${t(detail[2])}</p></div><div class="cropcure-orb">✦</div>`;
    nav.insertAdjacentElement('afterend', banner);
    const picker = document.createElement('label');
    picker.className = 'language-picker';
    picker.innerHTML = `Language <select><option value="English">English</option><option value="தமிழ்">தமிழ்</option><option value="हिन्दी">हिन्दी</option></select>`;
    nav.append(picker);
    const selector = picker.querySelector('select');
    selector.value = sessionStorage.getItem('cropcureLanguage') || 'English';
    const navLabels = ['home', 'detection', 'results', 'history', 'profile'];
    nav.querySelectorAll('.menu a').forEach((link, index) => { if (navLabels[index]) link.textContent = t(navLabels[index]); });
    selector.onchange = async () => {
      sessionStorage.setItem('cropcureLanguage', selector.value);
      try { await request('auth/profile/', {method: 'POST', body: JSON.stringify({language: selector.value})}); } catch (_) {}
      window.location.reload();
    };
    if (page === '/home.html') {
      const tribute = document.createElement('section');
      tribute.className = 'heritage-tribute';
      tribute.innerHTML = `<article><img src="https://upload.wikimedia.org/wikipedia/commons/d/d0/Nammalvar.G.jpg" alt="G. Nammalvar in a field"><div><h2>நம்மாழ்வார் · Nammalvar’s natural-farming legacy</h2><p>CropCure honours Tamil Nadu’s tradition of soil-first farming—observing plants closely, preserving biodiversity, and making careful decisions for every field.</p><small>Portrait: G. Nammalvar, Wikimedia Commons.</small></div></article>`;
      const homeHero = document.querySelector('.hero');
      if (homeHero) homeHero.insertAdjacentElement('afterend', tribute);
      else banner.insertAdjacentElement('afterend', tribute);
    }
  }
  // profile.html contains an old AngularJS prototype.  It is not connected to
  // Django authentication, so prevent it from redirecting over the live page.
  if (page.endsWith('/profile.html')) document.documentElement.removeAttribute('ng-app');
  if (page.endsWith('/home.html')) requireUser().catch(() => {});
  if (page.endsWith('/detection.html')) setupDetection().catch(() => {});
  if (page.endsWith('/recommend.html')) setupResults().catch(error => alert(error.message));
  if (page.endsWith('/history.html')) setupHistory().catch(error => alert(error.message));
  if (page.endsWith('/profile.html')) setupProfile().catch(() => {});
})();
