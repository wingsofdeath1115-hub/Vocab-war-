const form = document.getElementById('build-form');
const progress = document.getElementById('progress');
const link = document.getElementById('download');
const canvas = document.getElementById('preview');
const ctx = canvas.getContext('2d');

let animationTimer;

function getSelectedActions() {
  return [...form.querySelectorAll('fieldset input[type=checkbox]:checked')]
    .map((el) => el.value)
    .join(',');
}

function playSpritesheet(url, frameWidth = 128, frameHeight = 128, frames = 8) {
  const img = new Image();
  img.onload = () => {
    let frame = 0;
    let row = 0;
    clearInterval(animationTimer);
    animationTimer = setInterval(() => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.imageSmoothingEnabled = false;
      const sx = (frame % frames) * frameWidth;
      const sy = row * frameHeight;
      ctx.drawImage(img, sx, sy, frameWidth, frameHeight, 0, 0, canvas.width, canvas.height);
      frame = (frame + 1) % frames;
      if (frame === 0) row = (row + 1) % Math.max(1, img.height / frameHeight);
    }, 100);
  };
  img.src = url;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  progress.value = 10;
  link.hidden = true;

  const data = new FormData(form);
  data.set('actions', getSelectedActions());

  try {
    const response = await fetch('/api/build', { method: 'POST', body: data });
    if (!response.ok) throw new Error('Build failed');
    const result = await response.json();

    progress.value = 90;
    link.href = `/api/download/${result.job_id}`;
    link.hidden = false;
    link.textContent = 'Download ZIP';

    playSpritesheet(`/${result.spritesheet_path}`);
    progress.value = 100;
  } catch (err) {
    console.error(err);
    alert('Failed to generate asset.');
    progress.value = 0;
  }
});
