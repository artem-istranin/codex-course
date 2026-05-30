const TAU = Math.PI * 2;
const canvas = document.querySelector("#wheel");
const ctx = canvas.getContext("2d");
const participantsInput = document.querySelector("#participants");
const spinButton = document.querySelector("#spin");
const sampleButton = document.querySelector("#sample");
const resultEl = document.querySelector("#result");
const errorEl = document.querySelector("#error");
const wheelStage = document.querySelector(".wheel-stage");
const celebrationLayer = document.querySelector("#celebration-layer");
const winnerOverlay = document.querySelector("#winner-overlay");
const winnerOverlayName = document.querySelector("#winner-overlay-name");
const closeCelebrationButton = document.querySelector("#close-celebration");
const winnerList = document.querySelector("#winner-list");
const winnerHistoryEmpty = document.querySelector("#winner-history-empty");
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

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
let winners = [];
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

function clearCelebration() {
  celebrationLayer.replaceChildren();
  winnerOverlay.hidden = true;
  resultEl.classList.remove("winner-reveal");
}

function dismissCelebration() {
  clearCelebration();
  spinButton.focus();
}

function celebrateWinner(winner) {
  clearCelebration();
  winnerOverlayName.textContent = winner;
  winnerOverlay.hidden = false;
  resultEl.classList.add("winner-reveal");

  if (prefersReducedMotion.matches) {
    closeCelebrationButton.focus();
    return;
  }

  const confetti = Array.from({ length: 90 }, (_, index) => {
    const piece = document.createElement("i");
    const angle = (index / 90) * TAU + Math.random() * 0.35;
    const distance = 36 + Math.random() * 48;

    piece.className = "confetti";
    piece.style.setProperty("--confetti-color", colors[index % colors.length]);
    piece.style.setProperty("--confetti-x", `${50 + Math.cos(angle) * distance}vw`);
    piece.style.setProperty("--confetti-y", `${42 + Math.sin(angle) * distance}vh`);
    piece.style.setProperty("--confetti-rotation", `${360 + Math.random() * 900}deg`);
    piece.style.setProperty("--confetti-delay", `${Math.random() * 180}ms`);
    piece.style.setProperty("--confetti-duration", `${1150 + Math.random() * 900}ms`);
    return piece;
  });

  celebrationLayer.replaceChildren(...confetti);
  closeCelebrationButton.focus();
}

function renderWinners() {
  winnerList.replaceChildren(
    ...winners.map((winner) => {
      const item = document.createElement("li");
      item.textContent = winner;
      return item;
    }),
  );
  winnerHistoryEmpty.hidden = winners.length > 0;
}

function resetWinners() {
  winners = [];
  renderWinners();
}

function syncParticipants(names) {
  participants = names;
  participantsInput.value = names.join("\n");
  drawWheel(names);
}

function updateSpinAvailability() {
  spinButton.disabled = isSpinning || participants.length < 2;
}

function readyMessage() {
  if (!participants.length) {
    return "Add names and spin the wheel.";
  }

  return participants.length === 1 ? "Add at least one more participant." : "Ready to spin.";
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
    wheelStage.classList.remove("is-spinning");
    winners.push(winner);
    const remainingParticipants = names.filter((_, index) => index !== winnerIndex);

    if (remainingParticipants.length === 1) {
      winners.push(remainingParticipants[0]);
      syncParticipants([]);
      setResult(`Complete. Final winner: ${remainingParticipants[0]}`, true);
    } else {
      syncParticipants(remainingParticipants);
      setResult(`Winner: ${winner}`, true);
    }

    renderWinners();
    celebrateWinner(winner);
    isSpinning = false;
    sampleButton.disabled = false;
    updateSpinAvailability();
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
  clearCelebration();
  setError("");
  setResult("Spinning...");

  if (names.length < 2) {
    setResult("Add names and spin the wheel.");
    setError("Enter at least two participants.");
    updateSpinAvailability();
    return;
  }

  isSpinning = true;
  wheelStage.classList.add("is-spinning");
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
    animateToWinner(payload.winner_index, payload.participants, payload.winner);
  } catch (error) {
    isSpinning = false;
    wheelStage.classList.remove("is-spinning");
    sampleButton.disabled = false;
    updateSpinAvailability();
    setResult("Add names and spin the wheel.");
    setError(error.message || "Something went wrong. Try again.");
  }
}

participantsInput.addEventListener("input", () => {
  if (isSpinning) {
    return;
  }

  participants = parseParticipants();
  clearCelebration();
  resetWinners();
  setError("");
  setResult(readyMessage());
  drawWheel(participants);
  updateSpinAvailability();
});

spinButton.addEventListener("click", spin);
closeCelebrationButton.addEventListener("click", dismissCelebration);

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !winnerOverlay.hidden) {
    dismissCelebration();
  }
});

sampleButton.addEventListener("click", () => {
  if (isSpinning) {
    return;
  }

  participantsInput.value = ["Alice", "Bob", "Clara", "Dmitri", "Elena", "Fatima"].join("\n");
  participants = parseParticipants();
  clearCelebration();
  resetWinners();
  setError("");
  setResult("Ready to spin.");
  drawWheel(participants);
  updateSpinAvailability();
});

drawWheel(participants);
renderWinners();
updateSpinAvailability();
