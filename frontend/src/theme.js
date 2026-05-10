/*
Copyright (c) 2018 Roman Miroshnychenko <roman1972@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

import { Tooltip } from 'bootstrap';

const STORAGE_KEY = 'web-pdb-theme';

function get_theme_icon(theme) {
  if (theme === 'dark') {
    return 'bi bi-moon-fill';
  }
  return 'bi bi-sun-fill';
}

function get_toggle_title(theme) {
  if (theme === 'dark') {
    return 'Switch to light mode';
  }
  return 'Switch to dark mode';
}

function get_next_theme(current) {
  if (current === 'dark') {
    return 'light';
  }
  return 'dark';
}

function get_initial_theme() {
  const saved = localStorage.getItem(STORAGE_KEY);

  if (saved) {
    return saved;
  }
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

function apply_theme(theme) {
  const btn = document.getElementById('theme_toggle_btn'),
        icon = btn.querySelector('i'),
        send_btn = document.getElementById('send_btn'),
        tip = Tooltip.getInstance(btn),
        title = get_toggle_title(theme);

  document.documentElement.setAttribute('data-bs-theme', theme);
  icon.className = get_theme_icon(theme);
  btn.setAttribute('title', title);
  if (tip) {
    tip.setContent({ '.tooltip-inner': title });
  }
  if (theme === 'dark') {
    send_btn.classList.remove('btn-light');
    send_btn.classList.add('btn-dark');
  } else {
    send_btn.classList.remove('btn-dark');
    send_btn.classList.add('btn-light');
  }
}

function bind_theme_toggle() {
  document.getElementById('theme_toggle_btn').addEventListener('click', () => {
    const next = get_next_theme(document.documentElement.getAttribute('data-bs-theme'));

    localStorage.setItem(STORAGE_KEY, next);
    apply_theme(next);
  });
}

export { apply_theme, bind_theme_toggle, get_initial_theme };
