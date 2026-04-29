/**
 * Toggle the comments panel for a given resource card.
 * Called inline via onclick="toggleComments(id)".
 */
function toggleComments(resourceId) {
  const panel  = document.getElementById('comments-' + resourceId);
  const btn    = panel
    ? panel.closest('.card').querySelector('.comment-toggle-btn')
    : null;

  if (!panel) return;

  const isHidden = panel.hasAttribute('hidden');
  if (isHidden) {
    panel.removeAttribute('hidden');
    if (btn) btn.setAttribute('aria-expanded', 'true');
    // Focus the input if user is logged in
    const input = panel.querySelector('.comment-input');
    if (input) input.focus();
  } else {
    panel.setAttribute('hidden', '');
    if (btn) btn.setAttribute('aria-expanded', 'false');
  }
}