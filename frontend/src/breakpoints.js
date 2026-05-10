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

import { state } from './globals';
import { send_command } from './utils';

const PRE_SELECTOR = '#curr_file';

function apply_breakpoint_classes(env) {
  const code = env.element,
        pre = code && code.parentNode,
        rows = code && code.querySelector('.line-numbers-rows');
  if (!pre || pre.id !== 'curr_file' || !rows) {
    return;
  }
  state.breakpoints.forEach((lineNumber) => {
    const span = Prism.plugins.lineNumbers &&
      Prism.plugins.lineNumbers.getLine(pre, lineNumber);
    if (span) {
      span.classList.add('breakpoint');
    }
  });
}

function handle_line_click(event) {
  const span = event.target.closest('.line-numbers-rows > span');
  if (span) {
    const lineIndex = Array.from(span.parentNode.children).indexOf(span),
          lineNumber = lineIndex + 1,
          target = state.dirname + state.filename + ':' + lineNumber;
    if (span.classList.contains('breakpoint')) {
      send_command('cl ' + target);
    } else {
      send_command('b ' + target);
    }
  }
}

function bind_breakpoint_events() {
  Prism.hooks.add('complete', apply_breakpoint_classes);
  document.querySelector(PRE_SELECTOR)
    .addEventListener('click', handle_line_click);
}

function get_line_span(preElement, lineNumber) {
  if (Prism.plugins.lineNumbers) {
    return Prism.plugins.lineNumbers.getLine(preElement, lineNumber);
  }
  return null;
}

export { bind_breakpoint_events, get_line_span };
export default bind_breakpoint_events;
