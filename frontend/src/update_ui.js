/*
Copyright (c) 2017 Roman Miroshnychenko <roman1972@gmail.com>

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

var is_fetching = false;

function update_stdout(data) {
  state.console_history += data;
  let $stdout = $('#stdout');
  $stdout.text(state.console_history);
  Prism.highlightElement($stdout[0]);
  $('#console').scrollTop($('#console').prop('scrollHeight'));
}

function update_frame_data() {
  if (!is_fetching) {
    is_fetching = true;
    $.getJSON('/frame-data')
    .then((frame_data) => {
      state.frame_data = frame_data;
      let $curr_file = $('#curr_file'),
          $curr_file_code = $('#curr_file_code'),
          $globals = $('#globals'),
          $locals = $('#locals');
      $globals.text(state.frame_data.globals);
      Prism.highlightElement($globals[0]);
      $locals.text(state.frame_data.locals);
      Prism.highlightElement($locals[0]);
      $curr_file_code.text(state.frame_data.file_listing);
      $curr_file.attr('data-line', state.frame_data.current_line);
      Prism.highlightElement($curr_file_code[0]);
      if (frame_data.current_line != -1 &&
          (frame_data.filename != state.filename ||
            frame_data.current_line != state.current_line)) {
        state.filename = frame_data.filename;
        state.current_line = frame_data.current_line;
        $curr_file.scrollTop($(`#lineno_${state.current_line}`).offset().top -
           $curr_file.offset().top + $curr_file.scrollTop() - $curr_file.height() / 2);
      }
      is_fetching = false;
    });
  }
}

websocket.onmessage = (event) => {
  update_stdout(event.data);
  update_frame_data();
};

function init_stdout() {
  $.get('/console-history')
  .then((data) => {
    update_stdout(data);
  });
}

export { update_frame_data, init_stdout };
