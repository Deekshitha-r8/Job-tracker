// Auto-set today's date on add form
document.addEventListener('DOMContentLoaded', () => {
  const dateInput = document.querySelector('input[name="applied_date"]');
  if (dateInput && !dateInput.value) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
  }

  // Animate table rows on load
  const rows = document.querySelectorAll('.job-row');
  rows.forEach((row, i) => {
    row.style.opacity = '0';
    row.style.transform = 'translateY(10px)';
    row.style.transition = `opacity 0.3s ${i * 0.04}s ease, transform 0.3s ${i * 0.04}s ease`;
    setTimeout(() => {
      row.style.opacity = '1';
      row.style.transform = 'translateY(0)';
    }, 50);
  });
});
