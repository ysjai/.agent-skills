(function() {
  const WS_PROTOCOL = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
  const WS_URL = WS_PROTOCOL + window.location.host;
  const MAX_QUEUED_EVENTS = 100;
  let ws = null;
  let eventQueue = [];
  let reconnectDelay = 1000;
  let reconnectTimer = null;

  function setStatus(text) {
    const status = document.getElementById('connection-status');
    if (status) status.textContent = text;
  }

  function connect() {
    clearTimeout(reconnectTimer);
    setStatus('Connecting');
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setStatus('Connected');
      reconnectDelay = 1000;
      eventQueue.forEach((event) => ws.send(JSON.stringify(event)));
      eventQueue = [];
    };

    ws.onmessage = (message) => {
      try {
        const data = JSON.parse(message.data);
        if (data.type === 'reload') window.location.reload();
      } catch (error) {
        setStatus('Invalid server message');
      }
    };

    ws.onclose = () => {
      setStatus('Disconnected');
      reconnectTimer = setTimeout(connect, reconnectDelay);
      reconnectDelay = Math.min(reconnectDelay * 2, 30000);
    };

    ws.onerror = () => ws.close();
  }

  function sendEvent(event) {
    const record = { ...event, timestamp: Date.now() };
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(record));
    } else {
      eventQueue.push(record);
      if (eventQueue.length > MAX_QUEUED_EVENTS) eventQueue.shift();
    }
  }

  function updateIndicator(selected) {
    const indicator = document.getElementById('indicator-text');
    if (!indicator) return;

    if (selected.length === 0) {
      indicator.textContent = 'Click an option above, then return to the terminal';
      return;
    }

    const label = selected.length === 1
      ? (selected[0].querySelector('h3, .content h3, .card-body h3')?.textContent?.trim() || selected[0].dataset.choice)
      : String(selected.length);
    indicator.textContent = label + ' selected - return to terminal to continue';
  }

  document.addEventListener('click', (event) => {
    const target = event.target.closest('[data-choice]');
    if (!target) return;

    const container = target.closest('.options') || target.closest('.cards');
    const selected = container ? Array.from(container.querySelectorAll('.selected')) : [];
    updateIndicator(selected);

    sendEvent({
      type: 'click',
      text: target.textContent.trim(),
      choice: target.dataset.choice,
      id: target.id || null,
      selected: target.classList.contains('selected')
    });
  });

  window.selectedChoice = null;

  window.toggleSelect = function(element) {
    const container = element.closest('.options') || element.closest('.cards');
    const multi = container && container.dataset.multiselect !== undefined;

    if (container && !multi) {
      container.querySelectorAll('.option, .card').forEach((option) => option.classList.remove('selected'));
    }

    if (multi) element.classList.toggle('selected');
    else element.classList.add('selected');

    const selected = container ? Array.from(container.querySelectorAll('.selected')) : [element];
    window.selectedChoice = multi
      ? selected.map((option) => option.dataset.choice)
      : element.dataset.choice;
  };

  window.brainstorm = {
    send: sendEvent,
    choice: (value, metadata = {}) => sendEvent({ type: 'choice', ...metadata, choice: value })
  };

  connect();
})();
