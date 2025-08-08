const API_BASE = 'http://localhost:5050';
const USER_ID = 1; // Placeholder user ID

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('loadHabits').addEventListener('click', loadHabits);
  loadHeatmap();
  loadHabitSuccess();
});

function loadHabits() {
  fetch(`${API_BASE}/users/${USER_ID}/habits`)
    .then((response) => response.json())
    .then((data) => {
      const list = document.getElementById('habitList');
      list.innerHTML = '';
      data.forEach((habit) => {
        const li = document.createElement('li');
        li.textContent = habit.name;
        list.appendChild(li);
      });
    })
    .catch((err) => console.error('Error loading habits:', err));
}

function loadHeatmap() {
  const cal = new CalHeatmap();
  fetch(`${API_BASE}/users/${USER_ID}/success-log`)
    .then((res) => res.json())
    .then((data) => {
      const formatted = {};
      data.forEach((entry) => {
        const timestamp = new Date(entry.date).getTime() / 1000;
        formatted[timestamp] = entry.success_rate;
      });
      cal.paint({
        itemSelector: '#habit-heatmap',
        range: 12,
        domain: { type: 'month', gutter: 4 },
        subDomain: { type: 'day', radius: 4, width: 20, height: 20 },
        data: { source: formatted, type: 'json' },
        scale: {
          color: { type: 'linear', domain: [0, 100], range: ['#3a3a3a', '#81c784'] },
        },
        tooltip: true,
      });

      const ctx = document.getElementById('successChart').getContext('2d');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.map((d) => d.date),
          datasets: [
            {
              label: 'Daily Success Rate (%)',
              data: data.map((d) => d.success_rate),
              borderColor: '#1e88e5',
              backgroundColor: 'rgba(30, 136, 229, 0.2)',
              tension: 0.2,
            },
          ],
        },
        options: {
          scales: {
            x: { ticks: { color: '#e0e0e0' }, grid: { color: '#333' } },
            y: { ticks: { color: '#e0e0e0' }, grid: { color: '#333' } },
          },
          plugins: { legend: { labels: { color: '#e0e0e0' } } },
        },
      });
    })
    .catch((err) => console.error('Error loading heatmap data:', err));
}

function loadHabitSuccess() {
  fetch(`${API_BASE}/users/${USER_ID}/habits/success`)
    .then((res) => res.json())
    .then((data) => {
      const ctx = document.getElementById('habitChart').getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.map((h) => h.name),
          datasets: [
            {
              label: 'Success Rate (%)',
              data: data.map((h) => h.success_rate),
              backgroundColor: '#1e88e5',
            },
          ],
        },
        options: {
          scales: {
            x: { ticks: { color: '#e0e0e0' }, grid: { color: '#333' } },
            y: { ticks: { color: '#e0e0e0' }, grid: { color: '#333' } },
          },
          plugins: { legend: { labels: { color: '#e0e0e0' } } },
        },
      });
    })
    .catch((err) => console.error('Error loading habit success data:', err));
}
