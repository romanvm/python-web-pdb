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
import { state } from './globals';
import { send_command } from './utils';

function bind_key_events() {
  $(document).keydown((event) => {
    if (event.keyCode === 121) {
      send_command('n');
      return false;
    }
    else if (event.keyCode === 122 && !event.shiftKey) {
      send_command('s');
      return false;
    }
    else if (event.keyCode === 122 && event.shiftKey) {
      send_command('r');
      return false;
    }
    else if (event.keyCode === 119) {
      send_command('c');
      return false;
    }
  });

  $('#stdin').keydown((event) => {
    if (event.keyCode === 13) {
      $('#send_btn').click();
      return false;
    } else if (event.keyCode === 38) {
      state.history_index++;
      if (state.history_index >= state.command_history.length) {
        state.history_index = 0;
      }
      $('#stdin').val(state.command_history[state.history_index]);
      return false;
    } else if (event.keyCode === 40) {
      state.history_index--;
      if (state.history_index < 0) {
        state.history_index = state.command_history.length - 1;
      } else if (state.history_index >= state.command_history.length) {
        state.history_index = 0;
      }
      $('#stdin').val(state.command_history[state.history_index]);
      return false;
    }
  });

}

export default bind_key_events;
