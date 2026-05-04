const TAU = Math.PI * 2;
const canvas = document.querySelector("#wheel");
const ctx = canvas.getContext("2d");
const participantsInput = document.querySelector("#participants");
const spinButton = document.querySelector("#spin");
const sampleButton = document.querySelector("#sample");
const resultEl = document.querySelector("#result");
const errorEl = document.querySelector("#error");

const colors = [
  "#e33d3d",
  "#218277",
  "#f0b64f",
  "#3d6fb6",
  "#d65796",
  "#4f8f46",
  "#de7f38",
  "#6755b8",
];

let rotation = 0;
let participants = parseParticipants();
let isSpinning = false;

function parseParticipants() {
  return participantsInput.value
    .split(/\r?\n/)
    .map((name) => name.trim())
    .filter(Boolean);
}

function setError(message) {
  errorEl.textContent = message;
}

function setResult(message, hasWinner = false) {
  resultEl.textContent = message;
  resultEl.classList.toggle("has-winner", hasWinner);
}

function normalizeAngle(angle) {
  return ((angle % TAU) + TAU) % TAU;
}

function drawWheel(names = participants) {
  const size = canvas.width;
  const center = size / 2;
  const radius = center - 18;

  ctx.clearRect(0, 0, size, size);

  if (!names.length) {
    ctx.beginPath();
    ctx.arc(center, center, radius, 0, TAU);
    ctx.fillStyle = "#f8fafc";
    ctx.fill();
    ctx.strokeStyle = "#d8dee8";
    ctx.lineWidth = 4;
    ctx.stroke();
    ctx.fillStyle = "#647086";
    ctx.font = "700 28px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("Add participants", center, center);
    return;
  }

  const slice = TAU / names.length;

  names.forEach((name, index) => {
    const start = rotation + index * slice - Math.PI / 2;
    const end = start + slice;

    ctx.beginPath();
    ctx.moveTo(center, center);
    ctx.arc(center, center, radius, start, end);
    ctx.closePath();
    ctx.fillStyle = colors[index % colors.length];
    ctx.fill();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 4;
    ctx.stroke();

    ctx.save();
    ctx.translate(center, center);
    ctx.rotate(start + slice / 2);
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    ctx.fillStyle = "#ffffff";
    ctx.font = "800 24px system-ui, sans-serif";
    ctx.shadowColor = "rgba(23, 32, 51, 0.35)";
    ctx.shadowBlur = 4;
    ctx.fillText(shortenName(name), radius - 24, 0);
    ctx.restore();
  });

  ctx.beginPath();
  ctx.arc(center, center, 54, 0, TAU);
  ctx.fillStyle = "#ffffff";
  ctx.fill();
  ctx.strokeStyle = "#172033";
  ctx.lineWidth = 6;
  ctx.stroke();

  ctx.fillStyle = "#172033";
  ctx.font = "900 18px system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("SPIN", center, center);
}

function shortenName(name) {
  return name.length > 18 ? `${name.slice(0, 16)}...` : name;
}

function targetRotationForIndex(index, count) {
  const slice = TAU / count;
  return normalizeAngle(-(index + 0.5) * slice);
}

function animateToWinner(winnerIndex, names, winner) {
  const startRotation = rotation;
  const target = targetRotationForIndex(winnerIndex, names.length);
  const extraTurns = 6;
  const delta = normalizeAngle(target - normalizeAngle(startRotation));
  const endRotation = startRotation + extraTurns * TAU + delta;
  const duration = 4200;
  const startedAt = performance.now();

  function frame(now) {
    const progress = Math.min((now - startedAt) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 4);
    rotation = startRotation + (endRotation - startRotation) * eased;
    drawWheel(names);

    if (progress < 1) {
      requestAnimationFrame(frame);
      return;
    }

    rotation = target;
    drawWheel(names);
    isSpinning = false;
    spinButton.disabled = false;
    sampleButton.disabled = false;
    setResult(`Winner: ${winner}`, true);
  }

  requestAnimationFrame(frame);
}

async function spin() {
  if (isSpinning) {
    return;
  }

  const names = parseParticipants();
  participants = names;
  drawWheel(names);
  setError("");
  setResult("Spinning...");

  if (!names.length) {
    setResult("Add names and spin the wheel.");
    setError("Enter at least one participant.");
    return;
  }

  isSpinning = true;
  spinButton.disabled = true;
  sampleButton.disabled = true;

  try {
    const response = await fetch("/api/pick-winner", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ participants: names }),
    });

    if (!response.ok) {
      throw new Error("The winner could not be selected.");
    }

    const payload = await response.json();
    participants = payload.participants;
    participantsInput.value = payload.participants.join("\n");
    animateToWinner(payload.winner_index, payload.participants, payload.winner);
  } catch (error) {
    isSpinning = false;
    spinButton.disabled = false;
    sampleButton.disabled = false;
    setResult("Add names and spin the wheel.");
    setError(error.message || "Something went wrong. Try again.");
  }
}

participantsInput.addEventListener("input", () => {
  if (isSpinning) {
    return;
  }

  participants = parseParticipants();
  setError("");
  setResult(participants.length ? "Ready to spin." : "Add names and spin the wheel.");
  drawWheel(participants);
});

spinButton.addEventListener("click", spin);

sampleButton.addEventListener("click", () => {
  if (isSpinning) {
    return;
  }

  participantsInput.value = ["Alice", "Bob", "Clara", "Dmitri", "Elena", "Fatima"].join("\n");
  participants = parseParticipants();
  setError("");
  setResult("Ready to spin.");
  drawWheel(participants);
});

drawWheel(participants);
