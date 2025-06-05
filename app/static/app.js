// ================================
// Utility: Convert bytes to human-readable format
// ================================
function humanFileSize(bytes) {
  const thresh = 1024;
  if (Math.abs(bytes) < thresh) return bytes + ' B';

  const units = ['KB', 'MB', 'GB', 'TB'];
  let u = -1;
  do {
    bytes /= thresh;
    ++u;
  } while (Math.abs(bytes) >= thresh && u < units.length - 1);

  return bytes.toFixed(1) + ' ' + units[u];
}

// ================================
// Sort Files Utility
// ================================
function sortFiles(files, key = "name", asc = true) {
  return [...files].sort((a, b) => {
    let valA = a[key];
    let valB = b[key];

    if (key === "modified") {
      valA = new Date(valA);
      valB = new Date(valB);
    }

    if (key === "size") {
      return asc ? valA - valB : valB - valA;
    }

    return asc
      ? String(valA).localeCompare(String(valB), 'fr', { sensitivity: 'base' })
      : String(valB).localeCompare(String(valA), 'fr', { sensitivity: 'base' });
  });
}

// ================================
// Default Sort Configuration
// ================================
const defaultSort = {
  key: "name",
  asc: true,
};

function updateSortIcons() {
  document.querySelectorAll("#filesTable th.sortable").forEach(th => {
    th.classList.remove("asc", "desc");
    if (th.dataset.sortKey === defaultSort.key) {
      th.classList.add(defaultSort.asc ? "desc" : "asc");
    }
  });
}

// ================================
// Fetch & render files from the server
// ================================
let allFiles = [];

async function fetchFiles() {
  try {
    const res = await fetch('/api/files');
    if (!res.ok) throw new Error("Erreur réseau");

    allFiles = await res.json();

    // Tri par défaut
    const sortedFiles = sortFiles(allFiles, defaultSort.key, defaultSort.asc);

    // Appliquer filtre de recherche si présent
    applySearchFilter(sortedFiles);

    // Mettre à jour les icônes de tri
    updateSortIcons();
  } catch (err) {
    console.error("[fetchFiles] Échec :", err);
  }
}

function applySearchFilter(files) {
  const query = document.getElementById("fileSearch")?.value.toLowerCase() || "";

  const filtered = files.filter(file =>
    file.name.toLowerCase().includes(query)
  );

  renderFileTable(filtered);
}

// ================================
// Render the file list into the table
// ================================
function renderFileTable(files) {
  const tbody = document.querySelector("#filesTable tbody");
  tbody.innerHTML = "";

  files.forEach(file => {
    const tr = document.createElement("tr");

    // --- Name ---
    const tdName = document.createElement("td");
    tdName.textContent = file.name;
    tr.appendChild(tdName);

    // --- Size ---
    const tdSize = document.createElement("td");
    tdSize.textContent = humanFileSize(file.size);
    tr.appendChild(tdSize);

    // --- Modified Date ---
    const tdDate = document.createElement("td");
    tdDate.textContent = new Date(file.modified).toLocaleString('fr-FR', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
    tr.appendChild(tdDate);

    // --- Download Link ---
    const tdDownload = document.createElement("td");
    const link = document.createElement("a");
    link.href = `/download/${encodeURIComponent(file.name)}`;
    link.className = "btn-download";
    link.innerHTML = '<i class="fa fa-download"></i>';
    tdDownload.appendChild(link);
    tr.appendChild(tdDownload);

    // --- SHA-256 Copy Button ---
    const tdHash = document.createElement("td");
    const btn = createSHAButton(file.sha256, tdHash);
    tdHash.appendChild(btn);
    tr.appendChild(tdHash);

    tbody.appendChild(tr);
  });
}

// ================================
// Create SHA-256 button with hover preview & click-to-copy
// ================================
function createSHAButton(sha256, tdHash) {
  const btn = document.createElement("button");
  btn.textContent = "SHA-256";
  btn.className = "btn btn-warning btn-sm position-relative";
  btn.style.fontWeight = "bold";
  btn.style.cursor = "pointer";

  let preview = null;

  // --- Show SHA-256 on hover ---
  btn.addEventListener("mouseenter", () => {
    preview = document.createElement("div");
    preview.textContent = `SHA-256: ${sha256}`;
    preview.className = "sha-preview position-absolute bg-light border p-2 small rounded";
    preview.style.top = "-80px";
    preview.style.left = "0";
    preview.style.minWidth = "300px";
    preview.style.maxWidth = "400px";
    preview.style.zIndex = "1000";
    preview.style.wordWrap = "break-word";
    preview.style.whiteSpace = "normal";
    preview.style.fontFamily = "monospace";
    tdHash.appendChild(preview);
  });

  // --- Hide preview on mouse leave ---
  btn.addEventListener("mouseleave", () => {
    if (preview) {
      preview.remove();
      preview = null;
    }
  });

  // --- Copy SHA-256 on click with toast ---
  btn.addEventListener("click", () => {
    navigator.clipboard.writeText(sha256).then(() => {
      if (preview) {
        preview.remove();
        preview = null;
      }
      showToast("SHA-256 copié dans le presse-papier !");
    });
  });

  return btn;
}

// ================================
// Toast Notification
// ================================
function showToast(message) {
  const toast = document.createElement("div");
  toast.textContent = message;
  toast.className = "position-fixed bg-dark text-white px-3 py-2 rounded shadow";
  toast.style.bottom = "30px";
  toast.style.left = "50%";
  toast.style.transform = "translateX(-50%)";
  toast.style.zIndex = "1050";
  toast.style.fontSize = "0.9rem";
  toast.style.opacity = "0";
  toast.style.transition = "opacity 0.3s ease";

  document.body.appendChild(toast);
  requestAnimationFrame(() => {
    toast.style.opacity = "1";
  });

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 2000);
}

// ================================
// Setup Server-Sent Events (SSE)
// ================================
function setupSSE() {
  let retryDelay = 3000;
  let evtSource;

  function connect() {
    evtSource = new EventSource("/events");

    evtSource.onopen = () => {
      console.log("[SSE] Connected");
      retryDelay = 3000;
    };

    evtSource.onmessage = (event) => {
      if (event.data === "update") {
        console.log("[SSE] Update received");
        fetchFiles();
      }
    };

    evtSource.onerror = () => {
      console.error("[SSE] Connection lost, retrying in", retryDelay, "ms");
      evtSource.close();
      setTimeout(() => {
        retryDelay = Math.min(30000, retryDelay * 2);
        connect();
      }, retryDelay);
    };
  }

  connect();
}

// ================================
// Initial Load
// ================================
fetchFiles();

document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("fileSearch");

  // --- Gestion du tri ---
  document.querySelectorAll("#filesTable th.sortable").forEach(th => {
    th.addEventListener("click", () => {
      const key = th.dataset.sortKey;

      if (defaultSort.key === key) {
        defaultSort.asc = !defaultSort.asc;
      } else {
        defaultSort.key = key;
        defaultSort.asc = true;
      }

      const sorted = sortFiles(allFiles, defaultSort.key, defaultSort.asc);
      applySearchFilter(sorted);
      updateSortIcons();
    });
  });

  // --- Recherche dynamique ---
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      const sorted = sortFiles(allFiles, defaultSort.key, defaultSort.asc);
      applySearchFilter(sorted);
    });
  }

  // --- Initialisation des fichiers ---
  fetchFiles();
});

// ================================
// Fallback if SSE is not supported
// ================================
if (window.EventSource) {
  setupSSE();
} else {
  console.warn("EventSource not supported, using polling every 5s");
  setInterval(fetchFiles, 5000);
}