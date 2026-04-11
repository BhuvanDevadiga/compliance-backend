fetch("/dashboard/summary", {
  headers: {
    "Authorization": "Bearer " + localStorage.getItem("token")
  }
})
  .then(res => res.json())
  .then(data => {

    document.getElementById("readiness").innerText =
      (data.audit_readiness * 100).toFixed(1) + "%";

    document.getElementById("high").innerText = data.distribution.high;
    document.getElementById("medium").innerText = data.distribution.medium;
    document.getElementById("low").innerText = data.distribution.low;

    const table = document.getElementById("topRisks");
    table.innerHTML = "";

    data.top_risks.forEach(control => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${control.control_id}</td>
            <td>${control.risk_score}</td>
            <td class="risk-${control.risk_level.toLowerCase()}">
                ${control.risk_level}
            </td>
            <td>${control.action_required ? "⚠ Action Required" : "-"}</td>
        `;

        table.appendChild(row);
    });

  })
  .catch(err => {
      document.getElementById("readiness").innerText = "Error loading data";
      console.error(err);
  });
