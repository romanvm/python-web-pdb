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

import { websocket, state } from './globals';

function save_command_in_history(command) {
  state.history_index = -1;
  if (command !== '' && command !== state.command_history[0]) {
    state.command_history.unshift(command);
    if (state.command_history.length > 10) {
      state.command_history.pop();
    }
  }
}

function send_command(command) {
  if (websocket.readyState === websocket.OPEN) {
    websocket.send(command + '\n');
    return true;
  }
  return false;
}

function resize_console() {
  let con_height = $(window).height() - 490;
  if (con_height <= 240) {
    con_height = 240;
  }
  $('#console').height(con_height);
}

export { save_command_in_history, send_command, resize_console };
