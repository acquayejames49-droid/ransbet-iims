// Live dashboard: draws the charts and refreshes everything every 5 seconds.
// This polling is what makes the numbers update "in real time" — if another
// user records a sale, your dashboard reflects it within 5 seconds.

let salesChart, statusChart, categoryChart;

async function getJSON(url) {
  const res = await fetch(url);
  return res.json();
}

function initCharts() {
  salesChart = new Chart(document.getElementById("salesChart"), {
    type: "line",
    data: { labels: [], datasets: [{ label: "Sales (GHS)", data: [],
      borderColor: "#0d6efd", backgroundColor: "rgba(13,110,253,.15)",
      fill: true, tension: 0.3 }] },
    options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
  });

  statusChart = new Chart(document.getElementById("statusChart"), {
    type: "doughnut",
    data: { labels: ["In stock", "Low", "Reorder now"],
      datasets: [{ data: [0, 0, 0],
        backgroundColor: ["#198754", "#ffc107", "#dc3545"] }] },
    options: { plugins: { legend: { position: "bottom" } } }
  });

  categoryChart = new Chart(document.getElementById("categoryChart"), {
    type: "bar",
    data: { labels: [], datasets: [{ label: "Units in stock", data: [],
      backgroundColor: "#0dcaf0" }] },
    options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
  });
}

async function refresh() {
  try {
    const s = await getJSON("/api/summary");
    document.getElementById("stat-products").textContent = s.total_products;
    document.getElementById("stat-low").textContent = s.low_stock;
    document.getElementById("stat-revenue").textContent = s.today_revenue.toFixed(2);
    document.getElementById("stat-value").textContent = Math.round(s.stock_value);

    const trend = await getJSON("/api/sales-trend");
    salesChart.data.labels = trend.labels;
    salesChart.data.datasets[0].data = trend.data;
    salesChart.update();

    const status = await getJSON("/api/stock-status");
    statusChart.data.datasets[0].data = [status.ok, status.low, status.reorder];
    statusChart.update();

    const cat = await getJSON("/api/stock-by-category");
    categoryChart.data.labels = cat.labels;
    categoryChart.data.datasets[0].data = cat.data;
    categoryChart.update();

    const now = new Date();
    document.getElementById("updated-at").textContent =
      "· " + now.toLocaleTimeString();
  } catch (e) {
    console.error("Dashboard refresh failed:", e);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initCharts();
  refresh();
  setInterval(refresh, 5000); // every 5 seconds
});
