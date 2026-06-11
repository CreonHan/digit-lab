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
  const small = document.createElement("canvas");
  small.width = 28;
  small.height = 28;
  const smallCtx = small.getContext("2d", { willReadFrequently: true });
  smallCtx.fillStyle = "#000";
  smallCtx.fillRect(0, 0, 28, 28);
  smallCtx.drawImage(canvas, 0, 0, 28, 28);
  const imageData = smallCtx.getImageData(0, 0, 28, 28).data;
  const pixels = [];
  for (let i = 0; i < imageData.length; i += 4) {
    pixels.push(Math.round((imageData[i] + imageData[i + 1] + imageData[i + 2]) / 3));
  }
  return pixels;
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
