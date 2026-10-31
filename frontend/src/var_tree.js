/*
Copyright (c) 2026 Roman Miroshnychenko <roman1972@gmail.com>

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

import { state } from './globals';

// How long to wait for expanded children before showing an updated tree
const EXPAND_WAIT_MS = 300,
      generations = {
        globals: 0,
        locals: 0
      };

function node_key(scope, path) {
  return scope + ':' + JSON.stringify(path);
}

function create_placeholder(text) {
  const li = document.createElement('li');

  li.className = 'var-placeholder';
  li.setAttribute('role', 'none');
  li.textContent = text;
  return li;
}

function create_group(role) {
  const ul = document.createElement('ul');

  ul.className = 'var-group';
  ul.setAttribute('role', role);
  return ul;
}

function set_expanded(li, expanded) {
  const icon = li.querySelector(':scope > .var-row > .var-toggle');

  li.setAttribute('aria-expanded', String(expanded));
  if (expanded) {
    icon.className = 'var-toggle bi bi-chevron-down';
  } else {
    icon.className = 'var-toggle bi bi-chevron-right';
  }
}

function create_node(node, path) {
  const li = document.createElement('li'),
        name = document.createElement('span'),
        row = document.createElement('div'),
        toggle = document.createElement('i'),
        value = document.createElement('span');

  li.className = 'var-node';
  li.setAttribute('role', 'treeitem');
  li.dataset.path = JSON.stringify(path);
  row.className = 'var-row';
  row.title = node.type;
  toggle.className = 'var-toggle';
  name.className = 'var-name';
  name.textContent = node.name;
  value.className = 'var-value';
  // Prism.highlight escapes HTML special characters
  value.innerHTML = Prism.highlight(node.value, Prism.languages.python, 'python');
  row.append(toggle, name, ' = ', value);
  li.appendChild(row);
  if (node.expandable) {
    li.dataset.expandable = 'true';
    set_expanded(li, false);
  }
  return li;
}

function fetch_children(scope, path) {
  const params = new URLSearchParams();

  params.set('scope', scope);
  params.set('path', JSON.stringify(path));
  return fetch(`/variables?${params}`)
    .then((response) => response.json()
      .then((data) => {
        if (!response.ok) {
          throw new Error(data.error);
        }
        return data;
      }));
}

// Create a node element and check if it should be expanded
function build_node(scope, node, parent_path) {
  const node_path = parent_path.concat([node.key]),
        tree_item = create_node(node, node_path);

  return {
    expanded: node.expandable && state.expanded_vars.has(node_key(scope, node_path)),
    li: tree_item
  };
}

// Load children of a tree node and restore expansion state of its descendants
function expand_node(scope, li) {
  const group = create_group('group'),
        path = JSON.parse(li.dataset.path);

  set_expanded(li, true);
  group.appendChild(create_placeholder('Loading...'));
  li.appendChild(group);
  return fetch_children(scope, path)
    .then((data) => {
      const built = data.children.map((child) => build_node(scope, child, path)),
            items = built.map((item) => item.li);

      if (data.more > 0) {
        items.push(create_placeholder(`... ${data.more} more`));
      } else if (!items.length) {
        items.push(create_placeholder('(no members)'));
      }
      group.replaceChildren(...items);
      return Promise.all(built.filter((item) => item.expanded)
        .map((item) => expand_node(scope, item.li)));
    })
    .catch((error) => {
      group.replaceChildren(create_placeholder(`<${error.message}>`));
    });
}

function collapse_node(li) {
  const group = li.querySelector(':scope > .var-group');

  set_expanded(li, false);
  if (group) {
    group.remove();
  }
}

function handle_click(event) {
  const row = event.target.closest('.var-row'),
        scope = event.currentTarget.id;

  // Do not toggle nodes when a user selects text
  if (row && row.parentNode.dataset.expandable === 'true' &&
      window.getSelection().isCollapsed) {
    const item = row.parentNode,
          key = node_key(scope, JSON.parse(item.dataset.path));

    if (item.getAttribute('aria-expanded') === 'true') {
      state.expanded_vars.delete(key);
      collapse_node(item);
    } else {
      state.expanded_vars.add(key);
      expand_node(scope, item);
    }
  }
}

function wait(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

// Render variable nodes for "globals" or "locals" scope and restore expanded nodes
function render_var_tree(scope, nodes) {
  const built = (nodes || []).map((node) => build_node(scope, node, [])),
        container = document.getElementById(scope),
        generation = generations[scope] + 1,
        root = create_group('none');

  generations[scope] = generation;
  if (nodes === null) {
    root.appendChild(create_placeholder('No data available'));
  } else {
    root.replaceChildren(...built.map((item) => item.li));
  }
  // Wait a bit for expanded nodes to prevent flickering of the tree
  Promise.race([
    Promise.all(built.filter((item) => item.expanded)
      .map((item) => expand_node(scope, item.li))),
    wait(EXPAND_WAIT_MS)
  ]).then(() => {
    if (generation === generations[scope]) {
      const { scrollLeft, scrollTop } = container;
      container.replaceChildren(root);
      container.scrollLeft = scrollLeft;
      container.scrollTop = scrollTop;
    }
  });
}

function bind_var_tree_events() {
  document.getElementById('globals').addEventListener('click', handle_click);
  document.getElementById('locals').addEventListener('click', handle_click);
}

export { bind_var_tree_events, render_var_tree };
