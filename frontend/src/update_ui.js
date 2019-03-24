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

import $ from 'jquery';
import Prism from 'prismjs';
import 'prismjs/components/prism-python.js';
import 'prismjs/plugins/line-highlight/prism-line-highlight.js';
import './prism-line-numbers.js';

import 'prismjs/themes/prism-okaidia.css';
import 'prismjs/plugins/line-highlight/prism-line-highlight.css';
import 'prismjs/plugins/line-numbers/prism-line-numbers.css';

import { websocket, state } from './globals';

var wait_buffer = [];

function update_ui() {
  $.getJSON('/frame-data')
  .then((frame_data) => {
    state.breakpoints = frame_data.breakpoints;
    state.dirname = frame_data.dirname;
    $('#filename').text(frame_data.filename);
    $('#curr_line').text(frame_data.current_line);
    const $console = $('#console'),
        $curr_file = $('#curr_file'),
        $curr_file_code = $('#curr_file_code'),
        $globals = $('#globals'),
        $locals = $('#locals'),
        $stdout = $('#stdout');
    $globals.text(frame_data.globals);
    $locals.text(frame_data.locals);
    $stdout.text(frame_data.console_history);
    $console.scrollTop($console.prop('scrollHeight'));
    $curr_file_code.text(frame_data.file_listing);
    $curr_file.attr('data-line', frame_data.current_line);
    Prism.highlightAll();
    if (frame_data.current_line !== -1 &&
        (frame_data.filename !== state.filename ||
          frame_data.current_line !== state.current_line)) {
      state.filename = frame_data.filename;
      state.current_line = frame_data.current_line;
      // Modified from here: https://stackoverflow.com/questions/2905867/how-to-scroll-to-specific-item-using-jquery
      $curr_file.scrollTop($(`#lineno_${state.current_line}`).offset().top -
          $curr_file.offset().top + $curr_file.scrollTop() - $curr_file.height() / 2);
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
