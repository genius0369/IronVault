// Password generator
function generatePassword() {
  const chars =
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
  let pass = "";
  for (let i = 0; i < 16; i++) {
    pass += chars[Math.floor(Math.random() * chars.length)];
  }
  return pass;
}

// copy helper
function copyText(text) {
  navigator.clipboard.writeText(text);
  alert("Copied!");
}

// auto lock after 5 min
let lockTimer;
function resetLockTimer() {
  clearTimeout(lockTimer);
  lockTimer = setTimeout(() => {
    window.location.href = "/logout";
  }, 5 * 60 * 1000);
}

document.addEventListener("click", resetLockTimer);
document.addEventListener("keypress", resetLockTimer);
resetLockTimer();