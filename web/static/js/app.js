/**
 * app.js – main application entry point
 *
 * Wires together:
 *  - File upload / drag-and-drop
 *  - PresentationViewer (slide rendering)
 *  - VoiceController    (Web Speech API, mirrors original v5.3.1 commands)
 */

import { VoiceController } from './voice.js';
import { PresentationViewer } from './presentation.js';

// ─── DOM references ──────────────────────────────────────────────────────
const $uploadScreen      = document.getElementById('upload-screen');
const $presentationScreen= document.getElementById('presentation-screen');
const $dropZone          = document.getElementById('drop-zone');
const $fileInput         = document.getElementById('file-input');
const $uploadProgress    = document.getElementById('upload-progress');
const $progressFill      = document.getElementById('progress-fill');
const $progressLabel     = document.getElementById('progress-label');
const $errorToast        = document.getElementById('error-toast');
const $fileName          = document.getElementById('file-name');
const $btnVoice          = document.getElementById('btn-voice');
const $voiceStatus       = document.getElementById('voice-status');
const $langSelect        = document.getElementById('lang-select');
const $helpModal         = document.getElementById('help-modal');
const $btnHelp           = document.getElementById('btn-help');
const $btnHelpClose      = document.getElementById('btn-help-close');
const $btnFullscreen     = document.getElementById('btn-fullscreen');
const $btnBlackout       = document.getElementById('btn-blackout');
const $btnPanel          = document.getElementById('btn-panel');
const $btnNotes          = document.getElementById('btn-notes');
const $btnPen            = document.getElementById('btn-pen');
const $btnEraser         = document.getElementById('btn-eraser');
const $btnPointer        = document.getElementById('btn-pointer');
const $btnZoomIn         = document.getElementById('btn-zoom-in');
const $btnZoomOut        = document.getElementById('btn-zoom-out');
const $btnZoomReset      = document.getElementById('btn-zoom-reset');
const $btnNewUpload      = document.getElementById('btn-new-upload');
const $navPrev           = document.getElementById('nav-prev');
const $navNext           = document.getElementById('nav-next');

// ─── core instances ──────────────────────────────────────────────────────
const viewer = new PresentationViewer({
  onSlideChange: (current, total) => {
    document.getElementById('slide-counter').textContent = `${current} / ${total}`;
  },
});

const voice = new VoiceController({
  lang: 'en-US',
  continuous: true,
  onCommand:    handleVoiceCommand,
  onTranscript: (t) => setVoiceStatus(`"${t}"`),
  onStatus:     (s) => setVoiceStatus(s),
});

// ─── upload ───────────────────────────────────────────────────────────────

$dropZone.addEventListener('click',     () => $fileInput.click());
$dropZone.addEventListener('dragover',  (e) => { e.preventDefault(); $dropZone.classList.add('drag-over'); });
$dropZone.addEventListener('dragleave', ()  => $dropZone.classList.remove('drag-over'));
$dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  $dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) uploadFile(file);
});

$fileInput.addEventListener('change', () => {
  if ($fileInput.files[0]) uploadFile($fileInput.files[0]);
  $fileInput.value = '';
});

$btnNewUpload.addEventListener('click', () => {
  voice.stop();
  $presentationScreen.classList.remove('active');
  $uploadScreen.style.display = 'flex';
});

async function uploadFile(file) {
  const form = new FormData();
  form.append('file', file);

  showProgress('Uploading…', 15);

  try {
    // Animate progress bar while waiting
    let pct = 15;
    const ticker = setInterval(() => {
      pct = Math.min(pct + 5, 85);
      showProgress('Processing…', pct);
    }, 300);

    const res = await fetch('/upload', { method: 'POST', body: form });
    clearInterval(ticker);

    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || 'Upload failed');

    showProgress('Done!', 100);
    await sleep(400);

    loadPresentation(data);
  } catch (err) {
    hideProgress();
    showError(err.message);
  }
}

function loadPresentation(data) {
  hideProgress();
  $fileName.textContent = data.filename;
  viewer.load(data.slides);

  $uploadScreen.style.display = 'none';
  $presentationScreen.classList.add('active');
}

// ─── voice commands ───────────────────────────────────────────────────────

function handleVoiceCommand(cmd) {
  const label = document.createElement('span');
  label.className = 'action-tag';
  label.textContent = cmd.action.replace(/_/g, ' ');

  const msg = document.createElement('span');
  msg.textContent = ` "${cmd.text}"`;

  $voiceStatus.innerHTML = '';
  $voiceStatus.appendChild(label);
  $voiceStatus.appendChild(msg);

  switch (cmd.action) {
    case 'next_slide':  viewer.next(); break;
    case 'prev_slide':  viewer.prev(); break;
    case 'jump_slide':  viewer.jumpTo(cmd.slide); break;
    case 'first_slide': viewer.first(); break;
    case 'last_slide':  viewer.last(); break;
    case 'start_show':  viewer.toggleFullscreen(); break;
    case 'end_show':
      if (document.fullscreenElement) document.exitFullscreen?.();
      break;
    case 'blackout':    viewer.toggleBlackout(); break;
    case 'zoom_in':     viewer.zoomIn(); break;
    case 'zoom_out':    viewer.zoomOut(); break;
    case 'zoom_reset':  viewer.zoomReset(); break;
    case 'fullscreen':  viewer.toggleFullscreen(); break;
    case 'pen_tool':    activateDrawTool('pen'); break;
    case 'eraser':      activateDrawTool('eraser'); break;
    case 'pointer':     activateDrawTool('pointer'); break;
    default: break;
  }

  // auto-restart recognition after a recognised command so it keeps listening
  voice.enableAutoRestart();
}

// ─── voice UI ──────────────────────────────────────────────────────────

$btnVoice.addEventListener('click', () => {
  voice.toggle();
  $btnVoice.classList.toggle('listening', voice.listening);
});

$langSelect.addEventListener('change', () => {
  voice.setLang($langSelect.value);
});

function setVoiceStatus(text) {
  $voiceStatus.textContent = text;
  $btnVoice.classList.toggle('listening', voice.listening);
}

// ─── toolbar buttons ─────────────────────────────────────────────────────

$navPrev.addEventListener('click', () => viewer.prev());
$navNext.addEventListener('click', () => viewer.next());

$btnFullscreen.addEventListener('click', () => {
  viewer.toggleFullscreen();
  $btnFullscreen.classList.toggle('active', !!document.fullscreenElement);
});

document.addEventListener('fullscreenchange', () => {
  $btnFullscreen.classList.toggle('active', !!document.fullscreenElement);
});

$btnBlackout.addEventListener('click', () => {
  viewer.toggleBlackout();
  const on = document.getElementById('blackout-overlay').classList.contains('active');
  $btnBlackout.classList.toggle('active', on);
});

$btnPanel.addEventListener('click', () => {
  viewer.togglePanel();
  $btnPanel.classList.toggle('active');
});

$btnNotes.addEventListener('click', () => viewer.toggleNotes());

$btnZoomIn.addEventListener('click',    () => viewer.zoomIn());
$btnZoomOut.addEventListener('click',   () => viewer.zoomOut());
$btnZoomReset.addEventListener('click', () => viewer.zoomReset());

// draw tools
[$btnPen, $btnEraser, $btnPointer].forEach(btn => {
  btn.addEventListener('click', () => activateDrawTool(btn.dataset.tool));
});

function activateDrawTool(tool) {
  [$btnPen, $btnEraser, $btnPointer].forEach(b => b.classList.remove('active'));
  const map = { pen: $btnPen, eraser: $btnEraser, pointer: $btnPointer };
  map[tool]?.classList.add('active');
  switch (tool) {
    case 'pen':     viewer.setPenTool(); break;
    case 'eraser':  viewer.setEraser();  break;
    default:        viewer.setPointer(); break;
  }
}

// ─── help modal ───────────────────────────────────────────────────────────
$btnHelp.addEventListener('click',      () => $helpModal.classList.add('open'));
$btnHelpClose.addEventListener('click', () => $helpModal.classList.remove('open'));
$helpModal.addEventListener('click', (e) => {
  if (e.target === $helpModal) $helpModal.classList.remove('open');
});

// ─── progress / error helpers ─────────────────────────────────────────────

function showProgress(label, pct) {
  $uploadProgress.classList.add('visible');
  $progressLabel.textContent = label;
  $progressFill.style.width  = `${pct}%`;
}

function hideProgress() {
  $uploadProgress.classList.remove('visible');
  $progressFill.style.width = '0%';
}

let _errorTimer;
function showError(msg) {
  $errorToast.textContent = msg;
  $errorToast.classList.add('show');
  clearTimeout(_errorTimer);
  _errorTimer = setTimeout(() => $errorToast.classList.remove('show'), 5000);
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
