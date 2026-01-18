// Toggle invoice paid/unpaid via AJAX
async function togglePaid(id) {
  try {
    const res = await fetch(`/invoices/toggle/${id}`, { method: "POST" });
    if (res.ok) {
      const row = document.querySelector(`#inv-${id}`);
      const badge = row.querySelector(".badge");
      const isPaid = badge.classList.contains("bg-success");
      badge.textContent = isPaid ? "Unpaid" : "Paid";
      badge.classList.toggle("bg-success");
      badge.classList.toggle("bg-danger");
    }
  } catch (e) {
    console.error("Toggle failed", e);
  }
}
