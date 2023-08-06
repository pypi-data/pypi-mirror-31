$(document).ready(function() {
  
  // slugify
  
  $('input.slugify').each(function() {
    var target = $(this);
    target.after(' <a href="javascript:void(0)" rel="' + target.attr('id') + '" class="slugify">Odświeź</a>');
  });
  
  $('a.slugify').click(function() {
    var anchor = $(this);
    var target = $("#" + anchor.attr('rel'));
    var source = $("#" + target.attr('rel'));
    var maxlength = target.attr('maxlength');
    target.val(URLify(source.val(), maxlength));
  });
  
  // clear
  
  $('input.clear,textarea.clear').each(function() {
    var target = $(this);
    target.after(' <a href="javascript:void(0)" rel="' + target.attr('id') + '" class="clear">Wyczyść</a>');
  });
  $('a.clear').click(function() {
    var anchor = $(this);
    var target = $("#" + anchor.attr('rel'));
    target.val('');
  });
  
  // copy
  
  $('input.copy,textarea.copy').each(function() {
    var target = $(this);
    target.after(' <a href="javascript:void(0)" rel="' + target.attr('id') + '" class="copy">Kopiuj</a>');
  });
  $('a.copy').click(function() {
    var anchor = $(this);
    var target = $("#" + anchor.attr('rel'));
    var source = $("#" + target.attr('rel'));
    target.val(source.val());
  });
  $('input.copy_text,textarea.copy_text').each(function() {
    var target = $(this);
    target.after(' <a href="javascript:void(0)" rel="' + target.attr('id') + '" class="copy_text">Kopiuj</a>');
  });
  
  // copy_text
  
  $('a.copy_text').click(function() {
    var anchor = $(this);
    var target = $("#" + anchor.attr('rel'));
    var source = $("#" + target.attr('rel'));
    editor = tinyMCE.get(target.attr('rel'));
    editor.selection.select(editor.getBody(), true);
    target.val(editor.selection.getContent({format : 'text'}));
  });
  
  // count
  
  $('input.count').each(function() {
    var target = $(this);
    id = target.attr('id') + '_count';
    count = target.attr('maxlength') - target.val().length;
    target.after(' <span id="'+id+'" class="gray">'+count+'</span>');
  }).bind('change keyup focus blur', function() {
    var target = $(this);
    count = target.attr('maxlength') - target.val().length
    $('#' + target.attr('id') + '_count').text(count);
  });
  
  $('textarea.count').each(function() {
    var target = $(this);
    id = target.attr('id') + '_count';
    count = target.val().length;
    target.after(' <span id="'+id+'" class="gray">'+count+'</span>');
  }).bind('change keyup focus blur', function() {
    var target = $(this);
    count = target.val().length
    $('#' + target.attr('id') + '_count').text(count);
  });
  
  // sms
  
  $('textarea.sms').each(function() {
    var target = $(this);
    var length = target.val().length;
    var value = length + " (" + Math.ceil(length / 160.) + ")";
    target.after(' <span id="' + target.attr('id') + '_sms" class="gray">' + value + '</span>');
  }).bind('change keyup focus blur', function() {
    var target = $(this);
    length = target.val().length;
    count = length + " (" + Math.ceil(length / 160.) + ")";
    $('#' + target.attr('id') + '_sms').text(count);
  });
  
  var sms = function() {
    var target = $(this);
    var length = target.val().length;
    var value = length + " (" + Math.ceil(length / 160.) + ")";
    $('#' + target.attr('id') + '_sms').text(value);
  };

  // position
  
  $('#result_list,.tabular.inline-related').each(function() {
    // Set this to the name of the column holding the position
    var position_field = 'position';
    
    // Determine the column number of the position field
    var position_column = -1;
    var cols = $(this).find('tbody tr:first').children();
  
    for (i = 0; i < cols.length; i++) {
      inputs = $(cols[i]).find('input[name*=' + position_field + ']');
  
      if (inputs.length > 0) {
        // Found!
        position_column = i;
        break;
      }
    }
  
    if (position_column > 0) {
      // Hide position field
      $(this).find('tbody tr').each(function(index) {
        position_td = $(this).children()[position_column];
        input = $(position_td).children('input').first();
        input.hide();
        label = $('<strong>' + input.val() + '</strong>');
        $(position_td).addClass('handle').append(label);
      });
          
      // Determine sorted column and order
      if ($(this).hasClass('tabular')) {
        sort_order = 'asc';
      } else {
        sorted = $(this).find('thead th.sorted');
        if (sorted.length > 0) {
          sorted_col = $(this).find('thead th').index(sorted);
          sort_order = sorted.hasClass('descending') ? 'desc' : 'asc';
        } else {
          sort_order = null;
        }
      }
      
      if (sort_order != null) {
        // Some visual enhancements
        header = $(this).find('thead tr').children()[position_column];
        $(header).css('width', '1em');
        $(this).find('tbody .handle').css('cursor', 'move');
              
        // Make tbody > tr sortable
        $(this).find('tbody').sortable({
          axis: 'y',
          items: 'tr',
          handle: '.handle',
          forcePlaceholderSize: true,
          cursor: 'move',
          update: function(event, ui) {
            item = ui.item;
            items = $(this).find('tr').get();
      
             if(sort_order == 'desc') {
               // Reverse order
               items.reverse();
             }
      
            $(items).each(function(index) {
              position_td = $(this).children()[position_column];
              input = $(position_td).children('input').first();
              label = $(position_td).children('strong').first();
              index++;
              input.val(index);
              label.text(index);
            });
      
            // Update row classes
            $(this).find('tr').removeClass('row1').removeClass('row2');
            $(this).find('tr:even').addClass('row1');
            $(this).find('tr:odd').addClass('row2');
          }
        });
      }
    }
  });
  
});