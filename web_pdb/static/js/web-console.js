function write_to_console(endpoint, schedule_next)
{
  $.getJSON(
  {
    url: endpoint,
  })
  .done(function(data)
  {
    $('#stdout').text(data.history);
    var console_elem = document.getElementById('console');
    console_elem.scrollTop = console_elem.scrollHeight;
    $('#vars').text(data.variables);
    $('#filename').text(data.frame_data.filename);
    $('#curr_frame_code').text(data.frame_data.listing);
    if (data.frame_data.start_line != -1 && data.frame_data.curr_line != -1)
    {
      $('#curr_line').text(data.frame_data.curr_line);
      $('#curr_frame').attr('data-start', data.frame_data.start_line);
      var curr_line = data.frame_data.curr_line - data.frame_data.start_line + 1;
      $('#curr_frame').attr('data-line', curr_line);
      curr_frame_elem  = document.getElementById('curr_frame');
      var offset;
      if (curr_line >= 6)
      {
        offset = (curr_line - 6) / (data.frame_data.total_lines - 6);
      }
      else
      {
        offset = 0;
      }
      console.log(offset);
      curr_frame_elem.scrollTop = curr_frame_elem.scrollHeight * offset;
    }
    Prism.highlightAll();
    if (schedule_next)
    {
      setTimeout(function() { write_to_console(endpoint, true); }, 200);
    }
  })
  .fail(function(r, s, e)
  {
    if (e == 'Forbidden' && schedule_next)
    {
      setTimeout(function() { write_to_console(endpoint, true); }, 200);
    }
  });
}


function resize_console()
{
  var con_height = win_height = $(window).height() - 480;
  if (con_height <= 240)
  {
    con_height = 240;
  }
  $('#console').height(con_height);
}


$(function()
{
  var command_history = [];
  var history_index = -1;

  $('title').text('Web-PDB Console on ' + window.location.host);
  $('#host').html('Web-PDB Console on <em>' + window.location.host + '</em>');

  $('#send-btn').click(function()
  {
    var input = $('#stdin').val();
    history_index = -1;
    $.ajax(
    {
      url: 'input',
      data: input + '\n',
      method: 'POST'
    })
    .done(function()
    {
      if (input != '' && input != command_history[0])
      {
        command_history.unshift(input);
        if (command_history.length > 10)
        {
            command_history.pop();
        }
      }
      $('#stdin').val('');
    });
  });

  $('#stdin').keydown(function(args)
  {
    if (args.keyCode == 13)
    {
      $('#send-btn').click();
      return false;
    }
    else if (args.keyCode == 38)
    {
      history_index++;
      if (history_index >= command_history.length)
      {
        history_index = 0;
      }
      $('#stdin').val(command_history[history_index]);
      return false;
    }
    else if (args.keyCode == 40)
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
  resize_console();
  write_to_console('output/history', false);
  setTimeout(function() { write_to_console('output/update', true); }, 200);
});
