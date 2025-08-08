const API_BASE = 'http://localhost:5050';
let USER_ID = localStorage.getItem('userId');
if (!USER_ID) {
  window.location.href = 'signup.html';
}

let successChart;
let habitChart;

document.addEventListener('DOMContentLoaded', () => {
  document
    .getElementById('addHabitForm')
    .addEventListener('submit', addHabit);
  loadHabits();
  loadHeatmap();
  loadHabitSuccess();
  loadBestWorst();
});

function loadHabits() {
  fetch(`${API_BASE}/users/${USER_ID}/habits/status/today`)
    .then((response) => response.json())
    .then((data) => {
      const list = document.getElementById('habitList');
      list.innerHTML = '';
      data.forEach((habit) => {
        const li = document.createElement('li');
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = habit.checked;
        checkbox.addEventListener('change', () =>
          toggleHabit(habit.habit_id, checkbox.checked)
        );
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(' ' + habit.name));
        li.appendChild(label);
        list.appendChild(li);
      });
    })
    .catch((err) => console.error('Error loading habits:', err));
}

function toggleHabit(habitId, checked) {
  fetch(`${API_BASE}/users/${USER_ID}/habits/${habitId}/checked`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ checked }),
  })
    .then(() => {
      loadHabits();
      loadHeatmap();
      loadHabitSuccess();
      loadBestWorst();
    })
    .catch((err) => console.error('Error toggling habit:', err));
}

function addHabit(e) {
  e.preventDefault();
  const name = document.getElementById('habitName').value.trim();
  if (!name) return;
  fetch(`${API_BASE}/users/${USER_ID}/habits`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  })
    .then((res) => {
      if (!res.ok) {
        return res.json().then((d) => {
          throw new Error(d.error || 'Failed to add habit');
        });
      }
      return res.json();
    })
    .then(() => {
      document.getElementById('habitName').value = '';
      loadHabits();
      loadHeatmap();
      loadHabitSuccess();
      loadBestWorst();
    })
    .catch((err) => alert(err.message));
}

function loadBestWorst() {
  fetch(`${API_BASE}/users/${USER_ID}/habits/best-worst`)
    .then((res) => res.json())
    .then((data) => {
      const div = document.getElementById('bestWorst');
      if (!data.best_habit) {
        div.textContent = 'No habits yet.';
      } else {
        div.innerHTML = `<p><strong>Best:</strong> ${data.best_habit.name} (${data.best_habit.success_rate}%)</p>
        <p><strong>Worst:</strong> ${data.worst_habit.name} (${data.worst_habit.success_rate}%)</p>`;
      }
    })
    .catch((err) => console.error('Error loading best/worst habits:', err));
}

function loadHeatmap() {
  const cal = new CalHeatmap();
  document.getElementById('habit-heatmap').innerHTML = '';
  fetch(`${API_BASE}/users/${USER_ID}/success-log`)
    .then((res) => res.json())
    .then((data) => {
      if (data.length === 0) {
        document.getElementById('habit-heatmap').textContent = 'No activity yet.';
      } else {
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
      }

      const ctx = document.getElementById('successChart').getContext('2d');
      if (successChart) successChart.destroy();
      successChart = new Chart(ctx, {
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
      if (habitChart) habitChart.destroy();
      habitChart = new Chart(ctx, {
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
