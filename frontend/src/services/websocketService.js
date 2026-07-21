class WebSocketService {
  constructor() {
    this.channels = new Map();
    this.maxReconnectAttempts = 5;
    this.reconnectSchedule = [2000, 5000, 10000, 20000, 30000]; // 2s, 5s, 10s, 20s, 30s
  }

  _initChannelState(url) {
    return {
      socket: null,
      listeners: new Map(),
      connected: false,
      reconnectAttempts: 0,
      url: url,
      reconnectTimer: null,
    };
  }

  connect(channel, url) {
    if (!this.channels.has(channel)) {
      this.channels.set(channel, this._initChannelState(url));
    }

    const state = this.channels.get(channel);

    // Update the URL if a new one is provided
    if (url) state.url = url;

    // Guard: already open or connecting — don't open a second socket
    if (state.socket) {
      const rs = state.socket.readyState;
      if (rs === WebSocket.OPEN || rs === WebSocket.CONNECTING) return;
      // Socket exists but is CLOSING or CLOSED — clear it and reconnect
      state.socket = null;
    }

    if (!state.url) return;

    try {
      state.socket = new WebSocket(state.url);
    } catch (e) {
      state.connected = false;
      state.socket = null;
      this._reconnect(channel);
      return;
    }

    state.socket.onopen = () => {
      console.log(`✅ WebSocket Connected: ${channel}`);
      state.connected = true;
      state.reconnectAttempts = 0; // reset on successful open
      this.emit(channel, "connected");
    };

    state.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // Skip heartbeat pings — don't surface them to consumers
        if (data?.type === "ping") return;
        this.emit(channel, "message", data);
        if (data.type) {
          this.emit(channel, data.type, data);
        }
      } catch (_) {
        // Silently ignore malformed frames
      }
    };

    state.socket.onclose = (event) => {
      state.connected = false;
      state.socket = null;
      this.emit(channel, "disconnected");
      // Only reconnect if this wasn't an intentional clean close (code 1000)
      if (event.code !== 1000) {
        this._reconnect(channel);
      }
    };

    state.socket.onerror = () => {
      // onerror is always followed by onclose — let onclose handle reconnect
    };
  }

  _reconnect(channel) {
    const state = this.channels.get(channel);
    if (!state || !state.url) return;

    if (state.reconnectAttempts >= this.maxReconnectAttempts) {
      console.warn(`WebSocket ${channel}: max reconnect attempts reached. Will retry in 30s.`);
      state.reconnectTimer = setTimeout(() => {
        state.reconnectAttempts = 0; // reset counter for fresh round
        this.connect(channel, state.url);
      }, 30000);
      return;
    }

    const delay = this.reconnectSchedule[state.reconnectAttempts] || 30000;
    state.reconnectAttempts++;

    if (state.reconnectTimer) {
      clearTimeout(state.reconnectTimer);
    }

    console.log(`🔄 WebSocket ${channel}: reconnect attempt ${state.reconnectAttempts} in ${Math.round(delay / 1000)}s`);

    state.reconnectTimer = setTimeout(() => {
      this.connect(channel, state.url);
    }, delay);
  }

  disconnect(channel) {
    const state = this.channels.get(channel);
    if (!state) return;

    if (state.reconnectTimer) {
      clearTimeout(state.reconnectTimer);
      state.reconnectTimer = null;
    }

    if (state.socket) {
      // Null out handlers before closing so onclose doesn't trigger a reconnect
      state.socket.onclose = null;
      state.socket.onerror = null;
      state.socket.close(1000, "Intentional disconnect");
      state.socket = null;
    }

    state.connected = false;
    state.reconnectAttempts = 0;
  }

  disconnectAll() {
    for (const channel of this.channels.keys()) {
      this.disconnect(channel);
    }
  }

  send(channel, data) {
    const state = this.channels.get(channel);
    if (!state || !state.socket) return;

    if (state.socket.readyState !== WebSocket.OPEN) return;

    state.socket.send(JSON.stringify(data));
  }

  on(channel, event, callback) {
    if (!this.channels.has(channel)) {
      this.channels.set(channel, this._initChannelState(null));
    }

    const state = this.channels.get(channel);

    if (!state.listeners.has(event)) {
      state.listeners.set(event, []);
    }

    const existing = state.listeners.get(event);
    // Guard: don't register the same callback twice
    if (!existing.includes(callback)) {
      existing.push(callback);
    }
  }

  off(channel, event, callback) {
    const state = this.channels.get(channel);
    if (!state || !state.listeners.has(event)) return;

    state.listeners.set(
      event,
      state.listeners.get(event).filter((cb) => cb !== callback)
    );
  }

  emit(channel, event, payload) {
    const state = this.channels.get(channel);
    if (!state || !state.listeners.has(event)) return;

    // Iterate over a copy to avoid mutation bugs if a listener calls off()
    [...state.listeners.get(event)].forEach((cb) => cb(payload));
  }

  isConnected(channel) {
    const state = this.channels.get(channel);
    return state ? state.connected : false;
  }

  getConnection(channel) {
    const state = this.channels.get(channel);
    return state ? state.socket : null;
  }
}

export default new WebSocketService();