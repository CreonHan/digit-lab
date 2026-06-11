const canvas = document.querySelector("#draw-canvas");
const clearButton = document.querySelector("#clear-button");
const statusText = document.querySelector("#predict-status");
const predictionDigit = document.querySelector("#prediction-digit");
const bars = document.querySelector("#bars");
const ctx = canvas.getContext("2d", { willReadFrequently: true });

let drawing = false;
let lastPoint = null;
let pendingTimer = null;
let hasInk = false;

function resetCanvas() {
  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  hasInk = false;
  predictionDigit.textContent = "-";
  updateBars(new Array(10).fill(0));
}

function buildBars() {
  bars.innerHTML = "";
  for (let digit = 0; digit < 10; digit += 1) {
    const slot = document.createElement("div");
    slot.className = "bar-slot";
    slot.innerHTML = `
      <div class="bar-track"><div class="bar-fill" style="height: 2px"></div></div>
      <div class="bar-value">0%</div>
      <div class="bar-label">${digit}</div>
    `;
    bars.appendChild(slot);
  }
}

function updateBars(probabilities) {
  const maxValue = Math.max(...probabilities);
  [...bars.children].forEach((slot, index) => {
    const value = probabilities[index] || 0;
    const percentage = Math.round(value * 1000) / 10;
    slot.classList.toggle("winner", value === maxValue && maxValue > 0);
    slot.querySelector(".bar-fill").style.height = `${Math.max(2, value * 100)}%`;
    slot.querySelector(".bar-value").textContent = `${percentage}%`;
  });
}

function pointFromEvent(event) {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  return {
    x: (event.clientX - rect.left) * scaleX,
    y: (event.clientY - rect.top) * scaleY,
  };
}

function drawLine(from, to) {
  ctx.strokeStyle = "#fff";
  ctx.lineWidth = 28;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.beginPath();
  ctx.moveTo(from.x, from.y);
  ctx.lineTo(to.x, to.y);
  ctx.stroke();
  hasInk = true;
}

function schedulePredict() {
  clearTimeout(pendingTimer);
  pendingTimer = setTimeout(predict, 110);
}

function pixels28() {
  const bounds = inkBounds();
  if (!bounds) {
    return new Array(28 * 28).fill(0);
  }

  const normalized = document.createElement("canvas");
  normalized.width = 28;
  normalized.height = 28;
  const normalizedCtx = normalized.getContext("2d", { willReadFrequently: true });
  normalizedCtx.imageSmoothingEnabled = true;
  normalizedCtx.imageSmoothingQuality = "high";
  normalizedCtx.fillStyle = "#000";
  normalizedCtx.fillRect(0, 0, 28, 28);

  const sourceWidth = bounds.maxX - bounds.minX + 1;
  const sourceHeight = bounds.maxY - bounds.minY + 1;
  const scale = 20 / Math.max(sourceWidth, sourceHeight);
  const targetWidth = Math.max(1, Math.round(sourceWidth * scale));
  const targetHeight = Math.max(1, Math.round(sourceHeight * scale));
  const targetX = Math.round((28 - targetWidth) / 2);
  const targetY = Math.round((28 - targetHeight) / 2);

  normalizedCtx.drawImage(
    canvas,
    bounds.minX,
    bounds.minY,
    sourceWidth,
    sourceHeight,
    targetX,
    targetY,
    targetWidth,
    targetHeight,
  );

  const centered = centerByMass(normalized);
  const imageData = centered.getContext("2d", { willReadFrequently: true }).getImageData(0, 0, 28, 28).data;
  const pixels = [];
  for (let i = 0; i < imageData.length; i += 4) {
    pixels.push(Math.round((imageData[i] + imageData[i + 1] + imageData[i + 2]) / 3));
  }
  return pixels;
}

function inkBounds() {
  const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
  let minX = canvas.width;
  let minY = canvas.height;
  let maxX = -1;
  let maxY = -1;

  for (let y = 0; y < canvas.height; y += 1) {
    for (let x = 0; x < canvas.width; x += 1) {
      const index = (y * canvas.width + x) * 4;
      const value = (data[index] + data[index + 1] + data[index + 2]) / 3;
      if (value > 12) {
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);
      }
    }
  }

  if (maxX < 0) {
    return null;
  }

  return {
    minX: Math.max(0, minX - 6),
    minY: Math.max(0, minY - 6),
    maxX: Math.min(canvas.width - 1, maxX + 6),
    maxY: Math.min(canvas.height - 1, maxY + 6),
  };
}

function centerByMass(sourceCanvas) {
  const sourceCtx = sourceCanvas.getContext("2d", { willReadFrequently: true });
  const imageData = sourceCtx.getImageData(0, 0, 28, 28);
  const data = imageData.data;
  let mass = 0;
  let sumX = 0;
  let sumY = 0;

  for (let y = 0; y < 28; y += 1) {
    for (let x = 0; x < 28; x += 1) {
      const index = (y * 28 + x) * 4;
      const value = (data[index] + data[index + 1] + data[index + 2]) / 3;
      mass += value;
      sumX += x * value;
      sumY += y * value;
    }
  }

  if (mass <= 0) {
    return sourceCanvas;
  }

  const shiftX = Math.round(14 - sumX / mass);
  const shiftY = Math.round(14 - sumY / mass);
  if (shiftX === 0 && shiftY === 0) {
    return sourceCanvas;
  }

  const shifted = document.createElement("canvas");
  shifted.width = 28;
  shifted.height = 28;
  const shiftedCtx = shifted.getContext("2d", { willReadFrequently: true });
  shiftedCtx.fillStyle = "#000";
  shiftedCtx.fillRect(0, 0, 28, 28);
  shiftedCtx.drawImage(sourceCanvas, shiftX, shiftY);
  return shifted;
}

async function predict() {
  if (!hasInk) {
    return;
  }
  statusText.textContent = "识别中...";
  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        pixels: pixels28(),
        thumbnail: canvas.toDataURL("image/png"),
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "识别失败");
    }
    predictionDigit.textContent = payload.predicted_digit;
    updateBars(payload.probabilities);
    statusText.textContent = "继续书写会实时更新概率";
  } catch (error) {
    statusText.textContent = error.message;
  }
}

canvas.addEventListener("pointerdown", (event) => {
  drawing = true;
  canvas.setPointerCapture(event.pointerId);
  lastPoint = pointFromEvent(event);
  drawLine(lastPoint, lastPoint);
  schedulePredict();
});

canvas.addEventListener("pointermove", (event) => {
  if (!drawing) {
    return;
  }
  const point = pointFromEvent(event);
  drawLine(lastPoint, point);
  lastPoint = point;
  schedulePredict();
});

canvas.addEventListener("pointerup", () => {
  drawing = false;
  lastPoint = null;
  schedulePredict();
});

canvas.addEventListener("pointercancel", () => {
  drawing = false;
  lastPoint = null;
});

clearButton.addEventListener("click", resetCanvas);

buildBars();
resetCanvas();
