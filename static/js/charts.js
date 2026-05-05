document.addEventListener("DOMContentLoaded", () => {
  const dailyCanvas = document.getElementById("dailyChart");
  const categoryCanvas = document.getElementById("categoryChart");
  const monthlyCanvas = document.getElementById("monthlyChart");

  if (!dailyCanvas && !categoryCanvas && !monthlyCanvas) {
    return;
  }

  fetch("/chart-data")
    .then((response) => response.json())
    .then((data) => {
      if (dailyCanvas) {
        new Chart(dailyCanvas, {
          type: "bar",
          data: {
            labels: data.daily_labels,
            datasets: [
              {
                label: "Daily Spending",
                data: data.daily_totals,
                backgroundColor: "rgba(59, 130, 246, 0.7)",
                borderRadius: 10,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } },
          },
        });
      }

      if (categoryCanvas) {
        new Chart(categoryCanvas, {
          type: "bar",
          data: {
            labels: data.category_labels,
            datasets: [
              {
                label: "Category Spending",
                data: data.category_totals,
                backgroundColor: [
                  "#2563eb",
                  "#0f766e",
                  "#f59e0b",
                  "#ef4444",
                  "#8b5cf6",
                  "#14b8a6",
                  "#ec4899",
                ],
                borderRadius: 8,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: { legend: { display: true } },
            scales: { y: { beginAtZero: true } },
          },
        });
      }

      if (monthlyCanvas) {
        new Chart(monthlyCanvas, {
          type: "line",
          data: {
            labels: data.monthly_labels,
            datasets: [
              {
                label: "Monthly Trend",
                data: data.monthly_totals,
                borderColor: "#0f766e",
                backgroundColor: "rgba(15, 118, 110, 0.15)",
                tension: 0.35,
                fill: true,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } },
          },
        });
      }
    })
    .catch(() => {
      // Silent fail to keep the page usable if the API is unavailable.
    });
});
