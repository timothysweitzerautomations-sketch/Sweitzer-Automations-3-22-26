const form = document.getElementById("form");
const portInput = document.getElementById("port");
const status = document.getElementById("status");

chrome.storage.sync.get({ port: 8765 }, (cfg) => {
  portInput.value = String(cfg.port);
});

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const port = parseInt(portInput.value, 10);
  if (Number.isNaN(port) || port < 1024 || port > 65535) {
    status.textContent = "Enter a valid port (1024–65535).";
    status.style.color = "#b91c1c";
    return;
  }
  chrome.storage.sync.set({ port }, () => {
    status.textContent = "Saved.";
    status.style.color = "#15803d";
  });
});
