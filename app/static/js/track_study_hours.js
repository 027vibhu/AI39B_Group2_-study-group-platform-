let seconds = 0;
let timer = null;

const timerDisplay = document.getElementById("timerDisplay");
const startBtn = document.getElementById("startBtn");
const pauseBtn = document.getElementById("pauseBtn");
const resetBtn = document.getElementById("resetBtn");

function updateTimer() {

    let hrs = Math.floor(seconds / 3600);
    let mins = Math.floor((seconds % 3600) / 60);
    let secs = seconds % 60;

    timerDisplay.innerText =
        String(hrs).padStart(2, '0') + ":" +
        String(mins).padStart(2, '0') + ":" +
        String(secs).padStart(2, '0');
}

startBtn.addEventListener("click", () => {

    if (!timer) {

        timer = setInterval(() => {
            seconds++;
            updateTimer();
        }, 1000);

    }
});

pauseBtn.addEventListener("click", () => {

    clearInterval(timer);
    timer = null;

});

resetBtn.addEventListener("click", () => {

    clearInterval(timer);
    timer = null;

    seconds = 0;

    updateTimer();
});