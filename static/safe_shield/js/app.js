document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('securityChart');
  if (ctx) {
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Threat exposure score',
          data: [72, 76, 69, 81, 88, 94],
          backgroundColor: ['#2dd4bf', '#22c55e', '#38bdf8', '#34d399', '#818cf8', '#10b981'],
          borderRadius: 8
        }]
      },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100 } } }
    });
  }
});
