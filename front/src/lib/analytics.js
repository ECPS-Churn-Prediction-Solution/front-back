function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (crypto.getRandomValues(new Uint8Array(1))[0] & 0xf) >> 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function getAnonId() {
  try {
    let v = localStorage.getItem('anon_id');
    if (!v) {
      v = uuidv4();
      localStorage.setItem('anon_id', v);
    }
    return v;
  } catch {
    return undefined;
  }
}

function getSessionId() {
  try {
    let v = sessionStorage.getItem('session_id');
    if (!v) {
      v = uuidv4();
      sessionStorage.setItem('session_id', v);
    }
    return v;
  } catch {
    return undefined;
  }
}

export async function track(eventName, payload = {}, { keepalive = true } = {}) {
  try {
    const body = JSON.stringify({
      event_name: eventName,
      page_url: location.href,
      referrer: document.referrer || undefined,
      ...payload,
    });
    const headers = new Headers({ 'Content-Type': 'application/json' });
    const sid = getSessionId();
    const aid = getAnonId();
    headers.set('X-Request-Id', uuidv4());
    if (sid) headers.set('X-Session-Id', sid);
    if (aid) headers.set('X-Anon-Id', aid);
    await fetch('/log/track', { method: 'POST', headers, body, keepalive, credentials: 'include' });
  } catch (e) {
    // no-op
  }
}


