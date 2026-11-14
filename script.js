/* Hide the ChatGPT-added URL attribution parameter from the address bar, not the actual domain.
   Restrict cleanup to this specific auto-appended value; preserve unrelated URL parameters and all hashes. */
(function(){
  try {
    const url = new URL(window.location.href);
    if (url.searchParams.get('utm_source') === 'chatgpt.com') {
      url.searchParams.delete('utm_source');
      const newQuery = url.searchParams.toString();
      window.history.replaceState(window.history.state, '', url.pathname + (newQuery ? '?' + newQuery : '') + url.hash);
    }
  } catch (_) {}
})();

document.addEventListener('DOMContentLoaded',()=>{const menu=document.querySelector('#menu'),links=document.querySelector('#navlinks');if(menu&&links){menu.addEventListener('click',()=>{let o=links.classList.toggle('open');menu.setAttribute('aria-expanded',String(o));menu.textContent=o?'Close ✕':'Menu ☰'});links.querySelectorAll('a').forEach(x=>x.addEventListener('click',()=>{links.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.textContent='Menu ☰'}));document.addEventListener('keydown',e=>{if(e.key==='Escape'&&links.classList.contains('open')){links.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.textContent='Menu ☰';menu.focus()}})}const cards=[...document.querySelectorAll('.guidecard[data-cat]')];const search=document.querySelector('#guide-search');const filters=[...document.querySelectorAll('.filter')];let category='All';function update(){if(!cards.length)return;let q=(search?.value||'').toLowerCase().trim(),shown=0;cards.forEach(c=>{let ok=(category==='All'||c.dataset.cat===category)&&(c.dataset.search||'').includes(q);c.hidden=!ok;if(ok)shown++});const count=document.querySelector('#results');if(count)count.textContent=shown+' guide'+(shown===1?'':'s')+' found';const empty=document.querySelector('#empty');if(empty)empty.hidden=shown>0}search?.addEventListener('input',update);filters.forEach(f=>f.addEventListener('click',()=>{category=f.dataset.filter;filters.forEach(x=>x.setAttribute('aria-pressed',String(x===f)));update()}));update();const fsearch=document.querySelector('#faq-search');fsearch?.addEventListener('input',()=>{const q=fsearch.value.toLowerCase();document.querySelectorAll('.faqitem').forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(q))});const checks=[...document.querySelectorAll('.check input')];if(checks.length){const key='vifieldnotes-checklist-v1';let saved={};try{saved=JSON.parse(localStorage.getItem(key)||'{}')}catch{}checks.forEach(c=>{c.checked=!!saved[c.id];c.addEventListener('change',()=>{saved[c.id]=c.checked;try{localStorage.setItem(key,JSON.stringify(saved))}catch{}refresh()})});function refresh(){const n=checks.filter(c=>c.checked).length;document.querySelector('#check-progress').textContent=n+' / '+checks.length+' complete';document.querySelector('#check-meter').value=n}refresh();document.querySelector('#reset-checks')?.addEventListener('click',()=>{checks.forEach(c=>{c.checked=false;saved[c.id]=false});try{localStorage.setItem(key,JSON.stringify(saved))}catch{}refresh()})}});

/* Consent-first Google Analytics 4: site visitors can opt in or decline. */
(function(){
  const measurementId = 'G-R2X4W14SCX';
  const consentKey = 'vifieldnotes-analytics-consent-v1';
  function readConsent(){ try { return localStorage.getItem(consentKey); } catch { return null; } }
  function writeConsent(choice){ try { localStorage.setItem(consentKey,choice); } catch {} }
  function enableAnalytics(){
    if (window.__viAnalyticsEnabled) return;
    window.__viAnalyticsEnabled = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function(){ window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', measurementId, { anonymize_ip: true });
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
    document.head.appendChild(tag);
  }
  function hideBanner(){
    const banner = document.getElementById('vi-consent');
    if (banner) banner.remove();
  }
  function setConsent(choice){
    writeConsent(choice);
    hideBanner();
    if (choice === 'accepted') enableAnalytics();
    else if (window.__viAnalyticsEnabled) window.location.reload();
  }
  function showBanner(){
    if (document.getElementById('vi-consent')) return;
    const banner = document.createElement('section');
    banner.id = 'vi-consent';
    banner.setAttribute('role','region');
    banner.setAttribute('aria-label','Analytics privacy choices');
    banner.innerHTML = '<div><strong>Optional website analytics</strong><p>May we use Google Analytics to understand visits and improve our guides? You can decline; the site still works. Learn more in our <a href="/vi-fieldnotes/about/">privacy notes</a>.</p></div><div class="vi-consent-actions"><button type="button" data-choice="declined">Decline</button><button type="button" data-choice="accepted">Allow analytics</button></div>';
    banner.querySelectorAll('button[data-choice]').forEach(button => button.addEventListener('click', () => setConsent(button.dataset.choice)));
    document.body.appendChild(banner);
  }
  document.addEventListener('DOMContentLoaded',function(){
    const consent = readConsent();
    if (consent === 'accepted') enableAnalytics();
    else if (consent !== 'declined') showBanner();
  });
  window.viFieldnotesResetAnalyticsChoice = function(){
    try { localStorage.removeItem(consentKey); } catch {}
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', showBanner, {once:true});
    else showBanner();
  };
})();

/* VI Fieldnotes utilities and post-launch editorial freshness notices. */
document.addEventListener('DOMContentLoaded', function(){
  const nav=document.getElementById('navlinks');
  if(nav && !nav.querySelector('a[href="/vi-fieldnotes/tools/"]')){
    const a=document.createElement('a');a.href='/vi-fieldnotes/tools/';a.textContent='Tools';
    const cta=nav.querySelector('.navcta'); if(cta)nav.insertBefore(a,cta);else nav.appendChild(a);
  }
  const input=document.getElementById('vi-storage-value');
  const check=document.getElementById('vi-storage-check');
  const result=document.getElementById('vi-storage-result');
  function calculate(){
    if(!input || !result)return;
    const raw=input.value.trim(), n=Number(raw), target=212;
    if(!raw || !Number.isFinite(n) || n<0 || n>100000){
      result.textContent='Enter a valid available-space number between 0 and 100,000 GB.';return;
    }
    const num=new Intl.NumberFormat('en-US',{maximumFractionDigits:1});
    if(n>=target){
      result.textContent='Your entered free space ('+num.format(n)+' GB) meets the current 212 GB PlayStation Indonesia preparation advisory. Margin: '+num.format(n-target)+' GB. Actual installation and updates may differ; verify on your console.';
    }else{
      result.textContent='Based on your entry ('+num.format(n)+' GB), you need at least '+num.format(target-n)+' GB more to meet PlayStation Indonesia’s current 212 GB preparation guidance. Review Settings → Storage before deleting or buying anything.';
    }
  }
  check?.addEventListener('click',calculate);
  input?.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();calculate();}});
  const now=new Date();
  if((now.getFullYear()>2026 || (now.getFullYear()===2026 && (now.getMonth()>10 || (now.getMonth()===10 && now.getDate()>=19)))) && !document.getElementById('vi-date-advisory')){
    const notice=document.createElement('div');notice.className='vi-date-advisory';notice.id='vi-date-advisory';
    notice.innerHTML='<div class="wrap"><strong>Publication note:</strong> These guides were fact-checked before the scheduled 19 November 2026 launch. New game details may have changed. Verify current information at <a href="https://www.rockstargames.com/VI" target="_blank" rel="noopener noreferrer">Rockstar’s official website ↗</a>.</div>';
    const main=document.querySelector('main'); if(main)main.insertAdjacentElement('afterbegin',notice);
  }
});
