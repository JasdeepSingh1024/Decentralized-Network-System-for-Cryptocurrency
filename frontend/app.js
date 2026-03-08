const API_BASE = window.location.origin;

let myAddress = localStorage.getItem('wallet_address') || 'alice';

function el(id) {
  return document.getElementById(id);
}

function showResult(eltId, message, isError = false) {
  const elt = el(eltId);
  if (!elt) return;
  elt.textContent = message;
  elt.className = 'result show ' + (isError ? 'error' : 'success');
}

async function api(path, options = {}) {
  const res = await fetch(API_BASE + path, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = Array.isArray(data.detail) ? data.detail.map(d => d.msg || d).join(', ') : (data.detail || data.message || res.statusText);
    throw new Error(msg);
  }
  return data;
}

async function checkApi() {
  const status = el('apiStatus');
  try {
    const h = await fetch(API_BASE + '/health');
    const d = await h.json();
    const chainLabel = d.chain_valid === false ? ' · Invalid' : ' · Valid';
    status.textContent = `API OK · Chain: ${d.length || 0} blocks${chainLabel}`;
    status.className = 'api-status ' + (d.chain_valid === false ? 'invalid' : 'ok');
  } catch (e) {
    status.textContent = 'API offline';
    status.className = 'api-status err';
  }
}

function renderBlocks(chain) {
  const list = el('blockList');
  list.innerHTML = '';
  (chain || []).forEach((b) => {
    const div = document.createElement('div');
    div.className = 'block-item';
    div.innerHTML = `<strong>#${b.index}</strong> ${b.hash ? b.hash.slice(0, 16) + '…' : ''}`;
    list.appendChild(div);
  });
}

function renderPending(pending) {
  const list = el('pendingList');
  list.innerHTML = '';
  (pending || []).forEach((tx) => {
    const div = document.createElement('div');
    div.className = 'tx-item' + (tx.signature ? ' signed' : '');
    div.textContent = `${tx.sender} → ${tx.receiver}: ${tx.amount}`;
    list.appendChild(div);
  });
}

async function refreshChain() {
  try {
    const data = await api('/chain');
    el('chainLength').textContent = data.length;
    renderBlocks(data.chain);
  } catch (e) {
    el('chainLength').textContent = '—';
    renderBlocks([]);
  }
}

async function refreshPending() {
  try {
    const data = await api('/transactions/pending');
    renderPending(data.pending);
  } catch (e) {
    renderPending([]);
  }
}

async function refreshBalance() {
  try {
    const data = await api('/balance/' + encodeURIComponent(myAddress));
    el('balance').textContent = data.balance.toFixed(2);
  } catch (e) {
    el('balance').textContent = '—';
  }
}

function init() {
  el('myAddress').value = myAddress;

  el('copyAddress').onclick = () => {
    navigator.clipboard.writeText(myAddress);
    showResult('sendResult', 'Address copied', false);
    setTimeout(() => el('sendResult').classList.remove('show'), 1500);
  };

  el('newAddress').onclick = () => {
    myAddress = 'user_' + Math.random().toString(36).slice(2, 10);
    localStorage.setItem('wallet_address', myAddress);
    el('myAddress').value = myAddress;
    refreshBalance();
  };

  el('sendForm').onsubmit = async (e) => {
    e.preventDefault();
    const to = el('toAddress').value.trim();
    const amount = parseFloat(el('amount').value);
    if (!to || amount <= 0) return;
    try {
      await api('/transactions', {
        method: 'POST',
        body: JSON.stringify({ sender: myAddress, receiver: to, amount }),
      });
      showResult('sendResult', 'Transaction submitted.');
      el('toAddress').value = '';
      el('amount').value = '';
      refreshPending();
      refreshBalance();
    } catch (err) {
      showResult('sendResult', err.message, true);
    }
  };

  el('mineBtn').onclick = async () => {
    el('mineResult').classList.remove('show');
    try {
      const data = await api('/mine', {
        method: 'POST',
        body: JSON.stringify({ miner_address: myAddress }),
      });
      showResult('mineResult', `Block #${data.block.index} mined. Hash: ${data.block.hash.slice(0, 16)}…`, false);
      refreshChain();
      refreshPending();
      refreshBalance();
    } catch (err) {
      showResult('mineResult', err.message, true);
    }
  };

  el('refreshChain').onclick = () => {
    refreshChain();
    refreshPending();
    refreshBalance();
  };

  const demoInvalidSigBtn = el('demoInvalidSigBtn');
  if (demoInvalidSigBtn) {
    demoInvalidSigBtn.onclick = async () => {
      const box = el('demoInvalidSigBox');
      const iconEl = el('demoInvalidSigIcon');
      const titleEl = el('demoInvalidSigTitle');
      const detailEl = el('demoInvalidSigDetail');
      const step1 = el('demoStep1');
      const step2 = el('demoStep2');
      const step3 = el('demoStep3');
      if (!box) return;

      box.className = 'demo-result-box demo-result-pending';
      if (iconEl) iconEl.textContent = '⋯';
      if (titleEl) titleEl.textContent = 'Running demo…';
      if (detailEl) detailEl.textContent = '';
      if (step1) step1.classList.add('active');
      if (step2) step2.classList.remove('active');
      if (step3) step3.classList.remove('active');

      await new Promise(r => setTimeout(r, 300));
      if (step1) step1.classList.remove('active');
      if (step2) step2.classList.add('active');

      try {
        await api('/demo/try-invalid-signature', { method: 'POST' });
        box.className = 'demo-result-box demo-result-accepted';
        if (iconEl) iconEl.textContent = '⚠';
        if (titleEl) titleEl.textContent = 'Unexpected: accepted';
        if (detailEl) detailEl.textContent = 'This should not happen.';
      } catch (err) {
        box.className = 'demo-result-box demo-result-rejected';
        if (iconEl) iconEl.textContent = '✓';
        if (titleEl) titleEl.textContent = 'Rejected';
        if (detailEl) detailEl.textContent = err.message || 'Invalid transaction signature. The system correctly rejected the forged transaction.';
      }
      if (step2) step2.classList.remove('active');
      if (step3) step3.classList.add('active');
    };
  }

  checkApi();
  refreshChain();
  refreshPending();
  refreshBalance();
  setInterval(checkApi, 10000);
}

init();
