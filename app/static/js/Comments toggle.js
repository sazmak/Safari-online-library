function toggleComments(resourceId) {
  const panel = document.getElementById('comments-' + resourceId);
  if (!panel) return;

  const card  = panel.closest('.card');
  const btn   = card ? card.querySelector('.comment-toggle-btn') : null;
  const title = btn ? btn.dataset.title : '';

  const overlay   = document.getElementById('comments-modal-overlay');
  const modalBody = document.getElementById('comments-modal-body');
  const modalTitle = document.getElementById('comments-modal-title');

  if (!overlay || !modalBody) return;

  modalTitle.textContent = title || 'Комментарии';
  modalBody.innerHTML = '';
  modalBody.appendChild(panel.cloneNode(true));

  overlay.removeAttribute('hidden');
  overlay.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';

  const input = modalBody.querySelector('.comment-input');
  if (input) input.focus();
}

function closeCommentsModal() {
  const overlay = document.getElementById('comments-modal-overlay');
  if (!overlay) return;
  overlay.setAttribute('hidden', '');
  overlay.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') closeCommentsModal();
});

document.getElementById('comments-modal-overlay')?.addEventListener('click', function (e) {
  if (e.target === this) closeCommentsModal();
});
