/* ── 5G Slice Monitor — JavaScript ────────────────────────────────── */

// ── Help panel toggle ───────────────────────────────────────────────
function openHelp() {
    document.getElementById('help-panel').classList.add('open');
    document.getElementById('help-overlay').classList.add('open');
}

function closeHelp() {
    document.getElementById('help-panel').classList.remove('open');
    document.getElementById('help-overlay').classList.remove('open');
}

// ── Theme toggle ────────────────────────────────────────────────────
function _basePath() {
    var m = window.location.pathname.match(/^(\/preview\/[^/]+)/);
    return m ? m[1] : '';
}

function toggleTheme() {
    var html = document.documentElement;
    var current = html.getAttribute('data-theme') || 'light';
    var next = current === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', next);

    // Persist via session
    fetch(_basePath() + '/toggle-theme', { method: 'POST' })
        .catch(function() { /* non-critical */ });
}

// ── Close help on Escape ────────────────────────────────────────────
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeHelp();
    }
});
