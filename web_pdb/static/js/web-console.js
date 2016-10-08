/*
Copyright (c) 2016 Roman Miroshnychenko <romanvm@yandex.ua>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/
$(function()
{
  // Globals
  var command_history = [];
  var history_index = -1;
  var filename = '';
  var curent_line = -1;

  // Functions
  function send_command(command)
  {
    $('#stdin').val(command);
    $('#send_btn').click();
  }

  function write_to_console(endpoint, schedule_next)
  {
    $.getJSON(
    {
      url: endpoint,
    })
    .done(function(data)
    {
      $('#stdout').text(data.history);
      $('#console').scrollTop($('#console').prop('scrollHeight'));
      if (data.frame_data.curr_line != -1)
      {
        $('#globals').text(data.globals);
        $('#locals').text(data.locals);
        $('#filename').text(data.frame_data.filename);
        $('#curr_line').text(data.frame_data.curr_line);
        $('#curr_file_code').text(data.frame_data.listing);
        $('#curr_file').attr('data-line', data.frame_data.curr_line);
        if (data.frame_data.filename != filename || data.frame_data.curr_line != curent_line)
        {
          // Auto-scroll only if moved to another line
          filename = data.frame_data.filename;
          current_line = data.frame_data.curr_line;
          var offset;
          if (current_line >= 8)
          {
            offset = (current_line - 8) / data.frame_data.total_lines;
          }
          else
          {
            offset = 0;
          }
          $('#curr_file').scrollTop($('#curr_file').prop('scrollHeight') * offset);
        }
      }
      Prism.highlightAll();
      var line_spans = $('span.line-numbers-rows').children('span');
      var i;
      for (i = 0; i < line_spans.length; i++)
      {
        line_spans[i].id = 'lineno_' + (i + 1);
        line_spans[i].onclick = function(event)
        {
          var line_number = event.currentTarget.id.split('_')[1];
          if (event.currentTarget.className == 'breakpoint')
          {
            send_command('cl ' + data.frame_data.filename + ':' + line_number);
          }
          else
          {
            send_command('b ' + data.frame_data.filename + ':'+ line_number);
          }
        };
        if (data.frame_data.breaklist.indexOf(i + 1) != -1)
        {
          line_spans[i].className = 'breakpoint';
        }
      }
      if (schedule_next)
      {
        setTimeout(function() { write_to_console(endpoint, true); }, 333);
      }
    })
    .fail(function(r, s, e)
    {
      if (e == 'Forbidden' && schedule_next)
      {
        setTimeout(function() { write_to_console(endpoint, true); }, 333);
      }
    });
  }

  function resize_console()
  {
    var con_height = $(window).height() - 490;
    if (con_height <= 240)
    {
      con_height = 240;
    }
    $('#console').height(con_height);
  }

  // Button events
  $('#next_btn').click(function()
  {
    send_command('n');
  });

  $('#step_btn').click(function()
  {
    send_command('s');
  });

  $('#return_btn').click(function()
  {
    send_command('r');
  });

  $('#continue_btn').click(function()
  {
    send_command('c');
  });

  $('#up_btn').click(function()
  {
    send_command('u');
  });

  $('#down_btn').click(function()
  {
    send_command('d');
  });

  $('#where_btn').click(function()
  {
    send_command('w');
  });

  $('#help_btn').click(function()
  {
    $('#help_window').modal();
  });

  $('#send_btn').click(function()
  {
    var input = $('#stdin').val();
    $.ajax(
    {
      url: 'input',
      data: input + '\n',
      method: 'POST',
      contentType: 'text/plain; charset=UTF-8'
    })
    .done(function()
    {
      $('#stdin').val('');
      history_index = -1;
      if (input != '' && input != command_history[0])
      {
        command_history.unshift(input);
        if (command_history.length > 10)
        {
          command_history.pop();
        }
      }
    });
  });

  // Key events
  $(document).keydown(function(event)
  {
    if (event.keyCode == 121)
    {
      send_command('n');
      return false;
    }
    else if (event.keyCode == 122 && !event.shiftKey)
    {
      send_command('s');
      return false;
    }
    else if (event.keyCode == 122 && event.shiftKey)
    {
      send_command('r');
      return false;
    }
    else if (event.keyCode == 119)
    {
      send_command('c');
      return false;
    }
  });

  $('#stdin').keydown(function(event)
  {
    if (event.keyCode == 13)
    {
      $('#send_btn').click();
      return false;
    }
    else if (event.keyCode == 38)
    {
      history_index++;
      if (history_index >= command_history.length)
      {
        history_index = 0;
      }
      $('#stdin').val(command_history[history_index]);
      return false;
    }
    else if (event.keyCode == 40)
    {
      history_index--;
      if (history_index < 0)
      {
        history_index = command_history.length - 1;
      }
      else if (history_index >= command_history.length)
      {
        history_index = 0;
      }
      $('#stdin').val(command_history[history_index]);
      return false;
    }
  });

  $(window).resize(resize_console);

  // Main
  $('title').text('Web-PDB Console on ' + window.location.host);
  $('#host').html('Web-PDB Console on <em>' + window.location.host + '</em>');
  resize_console();
  write_to_console('output/history', false);
  setTimeout(function() { write_to_console('output/update', true); }, 333);
});
