const API_BASE = 'http://localhost:5050';

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('signupForm');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    try {
      const res = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('userId', data.user_id);
        window.location.href = 'index.html';
      } else {
        alert(data.error || 'Registration failed');
      }
    } catch (err) {
      console.error('Registration error:', err);
      alert('Registration failed');
    }
  });
});
