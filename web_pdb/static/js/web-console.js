function write_to_console(endpoint) {
    $.ajax({
    url: endpoint,
    method: 'GET'
  }).done(function(data) {
    $('#stdout').text(data);
    Prism.highlightAll();
    window.scrollTo(0, document.body.scrollHeight);
    var elem = document.getElementById('console');
    elem.scrollTop = elem.scrollHeight;
  });
}


function update_console() {
  write_to_console('output/update');
  setTimeout(update_console, 500);
}


$(function() {

  var command_history = [];
  var history_index = -1;

  var tile = 'Web-PDB Console on ' + window.location.host;
  $('title').text(tile)
  $('#host').text(tile);

  $('#send-btn').click(function() {
    var input = $('#stdin').val();
    history_index = -1;
    $.ajax({
      url: 'input',
      data: input + '\n',
      method: 'POST'
    }).done(function() {
      if (input != '' && input != command_history[0]) {
        command_history.unshift(input);
        if (command_history.length > 10) {
            command_history.pop();
        }
      }
      $('#stdin').val('');
    });
  });

  $('#stdin').keydown(function(args) {
    if (args.keyCode == 13) {
      $('#send-btn').click();
      return false;
    }
    else if (args.keyCode == 38) {
      history_index++;
      if (history_index >= command_history.length) {
        history_index = 0;
      }
      $('#stdin').val(command_history[history_index]);
      return false;
    }
    else if (args.keyCode == 40) {
      history_index--;
      if (history_index < 0) {
        history_index = command_history.length - 1;
      }
      else if (history_index >= command_history.length) {
        history_index = 0;
      }
      $('#stdin').val(command_history[history_index]);
      return false;
    }
  });

  write_to_console('output/history');

  setTimeout(update_console, 500);
});
