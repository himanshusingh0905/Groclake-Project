document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("fetchReport").addEventListener("click", function () {
        const fetchButton = document.getElementById("fetchReport");
        const loadingText = document.getElementById("loading");
        const container = document.getElementById("mainContainer");
        const introText = document.querySelector(".intro-text"); // Select the intro text

        // Hide the intro text
        if (introText) {
            introText.style.display = "none";
        }

        // Show loading animation
        loadingText.style.display = "block";

        // Expand container smoothly
        container.classList.add("expanded");

        // Hide button after clicking
        fetchButton.style.display = "none";

        // Fetch data (but don't delay UI updates)
        fetch("/get_health_recommendation")
            .then(response => response.json())
            .then(data => {
                // Hide loading animation
                loadingText.style.display = "none";

                if (data.error) {
                    alert("Error: " + data.error);
                    return;
                }

                // Show raw health data
                const tableBody = document.getElementById("dataTable").querySelector("tbody");
                tableBody.innerHTML = ""; // Clear previous data
                for (const key in data.raw_data) {
                    const row = tableBody.insertRow();
                    row.insertCell(0).textContent = key.replace(/_/g, " ").toUpperCase();
                    row.insertCell(1).textContent = data.raw_data[key];
                }
                document.getElementById("healthData").style.display = "block";

                // Show health report
                let reportContent = document.getElementById("reportContent");
                reportContent.innerHTML = ""; // Clear previous content

                for (const category in data.health_report) {
                    let section = document.createElement("div");
                    section.innerHTML = `<h3>${category.replace(/_/g, " ").toUpperCase()}</h3>
                     <p>${data.health_report[category]
                         .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // Convert **bold** to <strong>bold</strong>
                         .replace(/\n/g, "<br>")}</p>`;

                    reportContent.appendChild(section);
                }
                document.getElementById("healthReport").style.display = "block";
            })
            .catch(error => {
                console.error("Fetch error:", error);
                loadingText.style.display = "none"; // Hide loading if error occurs
            });
    });
});
