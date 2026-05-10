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

import Prism from 'prismjs';
import 'prismjs/components/prism-python.js';
import 'prismjs/plugins/line-highlight/prism-line-highlight.js';
import 'prismjs/plugins/line-numbers/prism-line-numbers.js';

import './prism-themes.css';
import 'prismjs/plugins/line-highlight/prism-line-highlight.css';
import 'prismjs/plugins/line-numbers/prism-line-numbers.css';

import { websocket, state } from './globals';
import { get_line_span } from './breakpoints';

const wait_buffer = [];

function update_ui() {
  fetch('/frame-data')
    .then((response) => response.json())
    .then((frame_data) => {
      const consoleEl = document.getElementById('console'),
            currFile = document.getElementById('curr_file');

      state.breakpoints = frame_data.breakpoints;
      state.dirname = frame_data.dirname;

      document.getElementById('filename').textContent = frame_data.filename;
      document.getElementById('curr_line').textContent = frame_data.current_line;
      document.getElementById('globals').textContent = frame_data.globals;
      document.getElementById('locals').textContent = frame_data.locals;
      document.getElementById('stdout').textContent = frame_data.console_history;
      document.getElementById('curr_file_code').textContent = frame_data.file_listing;

      consoleEl.scrollTop = consoleEl.scrollHeight;
      currFile.setAttribute('data-line', frame_data.current_line);

      Prism.highlightAll();

      if (frame_data.current_line !== -1 &&
          (frame_data.filename !== state.filename ||
            frame_data.current_line !== state.current_line)) {
        state.filename = frame_data.filename;
        state.current_line = frame_data.current_line;

        const lineSpan = get_line_span(currFile, state.current_line);
        if (lineSpan) {
          const fileRect = currFile.getBoundingClientRect(),
                lineRect = lineSpan.getBoundingClientRect();

          currFile.scrollTop += lineRect.top - fileRect.top - currFile.clientHeight / 2;
        }
      }
    });
}

websocket.onmessage = () => {
  // WebSocket receives only data update pings from the back-end so payload does not matter.
  // This method prevents firing bursts of requests to the back-end when it sends a series of pings.
  wait_buffer.push(null);
  setTimeout(() => {
    wait_buffer.pop();
    if (!wait_buffer.length) {
      update_ui();
    }
  }, 1);
};

export default update_ui;
