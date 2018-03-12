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
import globals from './globals';

function write_to_console(endpoint, schedule_next) {
  $.getJSON({
    url: endpoint,
  })
  .done((data) => {
    if (data) {
      let has_moved = false;
      $('#stdout').text(data.history);
      $('#console').scrollTop($('#console').prop('scrollHeight'));
      if (data.frame_data.curr_line != -1) {
        $('#globals').text(data.globals);
        $('#locals').text(data.locals);
        $('#filename').text(data.frame_data.filename);
        $('#curr_line').text(data.frame_data.curr_line);
        $('#curr_file_code').text(data.frame_data.listing);
        $('#curr_file').attr('data-line', data.frame_data.curr_line);
        if (data.frame_data.filename != globals.filename ||
            data.frame_data.curr_line != globals.current_line) {
          globals.filename = data.frame_data.filename;
          globals.current_line = data.frame_data.curr_line;
          has_moved = true
        }
      }
      globals.breaklist = data.frame_data.breaklist;
      Prism.highlightAll();
      // Auto-scroll only if moved to another line
      if (has_moved) {
        // Modified from here: https://stackoverflow.com/questions/2905867/how-to-scroll-to-specific-item-using-jquery
        let curr_file = $('#curr_file');
        curr_file.scrollTop($(`#lineno_${globals.current_line}`).offset().top -
          curr_file.offset().top + curr_file.scrollTop() - curr_file.height() / 2);
      }
    }
    if (schedule_next) {
      setTimeout(() => { write_to_console(endpoint, true); }, 333);
    }
  });
}

export default write_to_console;
