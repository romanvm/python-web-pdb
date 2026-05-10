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

import { state } from './globals';
import { send_command } from './utils';

function bind_key_events() {
  const stdin = document.getElementById('stdin');

  document.addEventListener('keydown', (event) => {
    if (event.key === 'F10') {
      send_command('n');
      event.preventDefault();
    } else if (event.key === 'F11' && !event.shiftKey) {
      send_command('s');
      event.preventDefault();
    } else if (event.key === 'F11' && event.shiftKey) {
      send_command('r');
      event.preventDefault();
    } else if (event.key === 'F8') {
      send_command('c');
      event.preventDefault();
    }
  });

  stdin.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      document.getElementById('send_btn').click();
      event.preventDefault();
    } else if (event.key === 'ArrowUp') {
      state.history_index++;
      if (state.history_index >= state.command_history.length) {
        state.history_index = 0;
      }
      stdin.value = state.command_history[state.history_index];
      event.preventDefault();
    } else if (event.key === 'ArrowDown') {
      state.history_index--;
      if (state.history_index < 0) {
        state.history_index = state.command_history.length - 1;
      } else if (state.history_index >= state.command_history.length) {
        state.history_index = 0;
      }
      stdin.value = state.command_history[state.history_index];
      event.preventDefault();
    }
  });
}

export default bind_key_events;
