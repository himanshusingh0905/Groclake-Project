document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("fetchReport").addEventListener("click", function () {
        fetch("/get_health_recommendation")  // Must match Flask route
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("Error: " + data.error);
                    return;
                }

                // Show raw health data
                const table = document.getElementById("dataTable");
                table.innerHTML = "";
                for (const key in data.raw_data) {
                    const row = table.insertRow();
                    row.insertCell(0).textContent = key.replace("_", " ").toUpperCase();
                    row.insertCell(1).textContent = data.raw_data[key];
                }
                document.getElementById("healthData").classList.remove("hidden");

                // Show health report
                document.getElementById("reportContent").innerHTML = `<p>${data.health_report.replace(/\n/g, "<br>")}</p>`;
                document.getElementById("healthReport").classList.remove("hidden");
            })
            .catch(error => console.error("Fetch error:", error));
    });
});
