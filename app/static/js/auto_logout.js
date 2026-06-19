/* Auto logout / token expiry frontend logic
   - idleLimit: seconds of inactivity before showing warning
   - warnDuration: seconds to count down before forced logout
   - keeps backend endpoints optional: POST /keepalive and GET /logout
*/
(function(){
  const idleLimit = 300; // 5 minutes before showing warning
  const warnDuration = 60; // 60s countdown once warning shows

  let lastActivity = Date.now();
  let warningTimer = null;
  let countdownTimer = null;

  const idleWarning = document.getElementById('idle-warning');
  const idleCountEl = document.getElementById('idle-count');
  const stayBtn = document.getElementById('stay-signed');
  const logoutBtn = document.getElementById('logout-now');
  const sessionIndicator = document.getElementById('session-time');

  function updateIndicator(text){ if(sessionIndicator) sessionIndicator.textContent = text }

  function resetTimers(){
    lastActivity = Date.now();
    hideWarning();
    scheduleWarning();
    updateIndicator('Active');
  }

  function scheduleWarning(){
    if(warningTimer) clearTimeout(warningTimer);
    const elapsed = (Date.now() - lastActivity);
    const ms = Math.max(0, idleLimit*1000 - elapsed);
    warningTimer = setTimeout(showWarning, ms);
  }

  function showWarning(){
    let remaining = warnDuration;
    if(idleCountEl) idleCountEl.textContent = remaining;
    if(idleWarning) idleWarning.classList.remove('hidden');
    updateIndicator('Idle — warning');
    countdownTimer = setInterval(()=>{
      remaining -= 1;
      if(idleCountEl) idleCountEl.textContent = remaining;
      if(remaining <= 0){
        clearInterval(countdownTimer);
        countdownTimer = null;
        doLogout();
      }
    }, 1000);
  }

  function hideWarning(){
    if(idleWarning) idleWarning.classList.add('hidden');
    if(countdownTimer){ clearInterval(countdownTimer); countdownTimer = null; }
  }

  function doLogout(){
    // Redirect to a logout endpoint — adjust if your app uses a different route
    window.location.href = '/logout';
  }

  if(stayBtn){
    stayBtn.addEventListener('click', ()=>{
      // inform server to extend session (optional)
      fetch('/keepalive', { method: 'POST', headers: { 'Content-Type':'application/json' } }).catch(()=>{}).finally(()=>{
        resetTimers();
      });
    });
  }

  if(logoutBtn){
    logoutBtn.addEventListener('click', ()=>{
      doLogout();
    });
  }

  // Activity events to reset idle timers
  const activityHandler = throttle(resetTimers, 500);
  ['mousemove','keydown','click','touchstart'].forEach(evt => document.addEventListener(evt, activityHandler, {passive:true}));

  document.addEventListener('visibilitychange', ()=>{ if(!document.hidden) resetTimers(); });

  // Simple throttle util
  function throttle(fn, wait){
    let last = 0;
    return function(...args){
      const now = Date.now();
      if(now - last > wait){ last = now; fn.apply(this, args); }
    }
  }

  // initialize
  scheduleWarning();
  updateIndicator('Active');

})();
