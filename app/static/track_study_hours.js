document.addEventListener("DOMContentLoaded", () => {
    const hoursInput = document.querySelector("#hours");
    const saveButton = document.querySelector("#saveSession");
    const totalHours = document.querySelector("#totalHours");
    const todayHours = document.querySelector("#todayHours");
    const progressBar = document.querySelector("#progressBar");

    let total = 0;
    let today = 0;
    const weeklyGoal = 20; // static goal for now

    saveButton.addEventListener("click", (e) => {
        e.preventDefault();
        const hours = parseFloat(hoursInput.value) || 0;

        total += hours;
        today += hours;

        totalHours.textContent = `${total} hrs`;
        todayHours.textContent = `${today} hrs`;

        // Update progress bar
        const progress = Math.min((total / weeklyGoal) * 100, 100);
        progressBar.style.width = progress + "%";

        // Change color based on progress
        if (progress < 50) {
            progressBar.style.background = "#27ae60"; // green
        } else if (progress < 100) {
            progressBar.style.background = "#f1c40f"; // yellow
        } else {
            progressBar.style.background = "#e74c3c"; // red
        }

        alert("Study session saved!");
        hoursInput.value = "";
    });
});
