// How to Create a Basic Plugin
// https://learn.jquery.com/plugins/basic-plugin-creation/

// Advanced Plugin Concepts
// https://learn.jquery.com/plugins/advanced-plugin-concepts/

// jQuery Plugin Boilerplate
// http://stefangabos.ro/jquery/jquery-plugin-boilerplate-revisited/

// viewport

(function($) {
  // @FG skasuj to, masz https://github.com/gabceb/jquery-browser-plugin
  // $.browser.desktop, $.browser.mobile
  $.viewport = function(mode, operator) {
    if (operator == undefined) operator = 'gte';
    var width = $(window).width();
    var mobile = 490;
    var tablet = 768;
    var desktop = 992;
    
    if (mode == 'mobile') {
      if (operator == 'lt') return width < mobile;
      else if (operator == 'lte') return width <= mobile;
      else if (operator == 'eq') return width == mobile;
      else if (operator == 'gt') return width > mobile;
      else if (operator == 'gte') return width >= mobile;
    } else if (mode == 'tablet') {
      if (operator == 'lt') return width < tablet;
      else if (operator == 'lte') return width <= tablet;
      else if (operator == 'eq') return width == tablet;
      else if (operator == 'gt') return width > tablet;
      else if (operator == 'gte') return width >= tablet;
    } else if (mode == 'desktop') {
      if (operator == 'lt') return width < desktop;
      else if (operator == 'lte') return width <= desktop;
      else if (operator == 'eq') return width == desktop;
      else if (operator == 'gt') return width > desktop;
      else if (operator == 'gte') return width >= desktop;
    }
    return false;
  };
})(jQuery);

// exists

(function($) {
  $.fn.exists = function() {
    return this.length > 0 ? this : false;
  };
})(jQuery);

// setDeviceScreen
// (function($) {
  // $.setDeviceScreen = function() {
    // $.get('/congo/maintenance/ajax/set-device-screen/', {screen_size: $(window).width()}, function(data) {
    // });
  // };
// })(jQuery);

// noCopyPaste

(function ($) {
  $.fn.noCopyPaste = function() {
    return this.bind("cut copy paste contextmenu", function(e) {
      e.preventDefault();
    });
  };
}(jQuery));

// notificationDismiss

(function($) {
  $.fn.notificationDismiss = function(settings) {
    var settings = jQuery.extend({
      timeout: 5000
    }, settings);
    
    this.each(function() {
      var div = $(this);
      setTimeout(function() {
        div.fadeOut();
      }, settings.timeout);
    });
  };
}(jQuery));

// notificationShow

(function($) {
  $.notificationShow = function(html, settings) {
    var settings = jQuery.extend({
      level: 'success',
      close: true,
      fade: true,
      inverted: false,
      dismiss: true,
      timeout: 5000,
      url: undefined,
    }, settings);
  
    document.getElementById('alert-notification-sound').play();
    
    if (settings.url) {
      var div = $('<div class="alert" style="cursor: pointer;" onclick="location.href='+ settings.url +'"></div>');
    } else {
      var div = $('<div class="alert"></div>');
    }
    
    div.addClass('alert-' + settings.level);
    if (settings.fade) div.addClass('fade').addClass('in');
    if (settings.inverted) div.addClass('alert-inverted');
    if (settings.close) div.append('<button data-dismiss="alert" class="close" type="button">&times;</button>');
    div.append('<div class="alert-icon"><i class="icon-' + settings.level + '"></i></div>');
    div.append('<div class="alert-body">' + html + '</div>');
    div.append('<div class="alert-progress"></div>');
    
      
    div.prependTo($('.notifications')).alert();
    
    if (settings.dismiss) {
      div.notificationDismiss({timeout: settings.timeout});
      var alertProgressbar = $('<div class="alert-progressbar"></div>');
      alertProgressbar.appendTo($('.alert-progress', div));
      alertProgressbar.animate({ width: '100%' }, settings.timeout);
    }
  };
}(jQuery));

// donetyping

(function($) {
  $.fn.extend({
    doneTyping: function(callback, timeout) {
      timeout = timeout || 1e3; // 1 second default timeout
      var timeoutReference, doneTyping = function(el) {
        if (!timeoutReference)
          return;
        timeoutReference = null;
        callback.call(el);
      };
      return this.each(function(i, el) {
        var $el = $(el);
        $el.is(':input') && $el.on('keyup keypress', function(e) {
          // This catches the backspace button in chrome, but also prevents
          // the event from triggering too premptively. Without this line,
          // using tab/shift+tab will make the focused element fire the callback.
          if (e.type == 'keyup' && e.keyCode != 8)
            return;

          // Check if timeout has been set. If it has, "reset" the clock and
          // start over again.
          if (timeoutReference)
            clearTimeout(timeoutReference);
          timeoutReference = setTimeout(function() {
            // if we made it here, our timeout has elapsed. Fire the
            // callback
            doneTyping(el);
          }, timeout);
        }).on('blur', function() {
          // If we can, fire the event since we're leaving the field
          doneTyping(el);
        });
      });
    }
  });
})(jQuery); 

