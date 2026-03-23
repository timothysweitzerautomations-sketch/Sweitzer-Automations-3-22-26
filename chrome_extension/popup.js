/**
 * Opens tabs to the local http.server serving revenue_pulse/ (same as python -m http.server).
 */
function baseUrl(port) {
  return `http://127.0.0.1:${port}`;
}

function openUrl(path) {
  const msg = document.getElementById("msg");
  msg.textContent = "";
  chrome.storage.sync.get({ port: 8765 }, (cfg) => {
    const url = `${baseUrl(cfg.port)}${path}`;
    chrome.tabs.create({ url }, () => {
      if (chrome.runtime.lastError) {
        msg.textContent = chrome.runtime.lastError.message || "Could not open tab.";
      }
    });
  });
}

document.getElementById("btnRevenue").addEventListener("click", () => {
  openUrl("/");
});

document.getElementById("btnFlip").addEventListener("click", () => {
  openUrl("/flip_tracker.html");
});

document.getElementById("linkOptions").addEventListener("click", (e) => {
  e.preventDefault();
  chrome.runtime.openOptionsPage();
});
