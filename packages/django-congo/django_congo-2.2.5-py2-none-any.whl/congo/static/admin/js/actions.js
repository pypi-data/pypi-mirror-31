/*global gettext, interpolate, ngettext*/
(function($) {
    'use strict';
    var lastChecked;

    $.fn.actions = function(opts) {
        var options = $.extend({}, $.fn.actions.defaults, opts);
        var actionCheckboxes = $(this);
        var list_editable_changed = false;
        var showQuestion = function() {
            $(options.acrossClears).hide();
            $(options.acrossQuestions).show();
            $(options.allContainer).hide();
        },
        showClear = function() {
            $(options.acrossClears).show();
            $(options.acrossQuestions).hide();
            $(options.actionContainer).toggleClass(options.selectedClass);
            $(options.allContainer).show();
            $(options.counterContainer).hide();
        },
        reset = function() {
            $(options.acrossClears).hide();
            $(options.acrossQuestions).hide();
            $(options.allContainer).hide();
            $(options.counterContainer).show();
        },
        clearAcross = function() {
            reset();
            $(options.acrossInput).val(0);
            $(options.actionContainer).removeClass(options.selectedClass);
        },
        checker = function(checked) {
            if (checked) {
                showQuestion();
            } else {
                reset();
            }
            $(actionCheckboxes).prop("checked", checked)
                .parent().parent().toggleClass(options.selectedClass, checked);
        },
        updateCounter = function() {
            var sel = $(actionCheckboxes).filter(":checked").length;
            // data-actions-icnt is defined in the generated HTML
            // and contains the total amount of objects in the queryset
            var actions_icnt = $('.action-counter').data('actionsIcnt');
            $(options.counterContainer).html(interpolate(
            ngettext('%(sel)s of %(cnt)s selected', '%(sel)s of %(cnt)s selected', sel), {
                sel: sel,
                cnt: actions_icnt
            }, true));
            $(options.allToggle).prop("checked", function() {
                var value;
                if (sel === actionCheckboxes.length) {
                    value = true;
                    showQuestion();
                } else {
                    value = false;
                    clearAcross();
                }
                return value;
            });
        };
        // Show counter by default
        $(options.counterContainer).show();
        // Check state of checkboxes and reinit state if needed
        $(this).filter(":checked").each(function(i) {
            $(this).parent().parent().toggleClass(options.selectedClass);
            updateCounter();
            if ($(options.acrossInput).val() === 1) {
                showClear();
            }
        });
        $(options.allToggle).show().click(function() {
            checker($(this).prop("checked"));
            updateCounter();
        });
        $("a", options.acrossQuestions).click(function(event) {
            event.preventDefault();
            $(options.acrossInput).val(1);
            showClear();
        });
        $("a", options.acrossClears).click(function(event) {
            event.preventDefault();
            $(options.allToggle).prop("checked", false);
            clearAcross();
            checker(0);
            updateCounter();
        });
        lastChecked = null;
        $(actionCheckboxes).click(function(event) {
            if (!event) { event = window.event; }
            var target = event.target ? event.target : event.srcElement;
            if (lastChecked && $.data(lastChecked) !== $.data(target) && event.shiftKey === true) {
                var inrange = false;
                $(lastChecked).prop("checked", target.checked)
                    .parent().parent().toggleClass(options.selectedClass, target.checked);
                $(actionCheckboxes).each(function() {
                    if ($.data(this) === $.data(lastChecked) || $.data(this) === $.data(target)) {
                        inrange = (inrange) ? false : true;
                    }
                    if (inrange) {
                        $(this).prop("checked", target.checked)
                            .parent().parent().toggleClass(options.selectedClass, target.checked);
                    }
                });
            }
            $(target).parent().parent().toggleClass(options.selectedClass, target.checked);
            lastChecked = target;
            updateCounter();
        });
        $('form#changelist-form table#result_list tr').find('td:gt(0) :input').change(function() {
            list_editable_changed = true;
        });
        $('form#changelist-form button[name="index"]').click(function(event) {
            if (list_editable_changed) {
                return confirm(gettext("You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost."));
            }
        });
        $('form#changelist-form input[name="_save"]').click(function(event) {
            var action_changed = false;
            $('select option:selected', options.actionContainer).each(function() {
                if ($(this).val()) {
                    action_changed = true;
                }
            });
            if (action_changed) {
                if (list_editable_changed) {
                    return confirm(gettext("You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action."));
                } else {
                    return confirm(gettext("You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button."));
                }
            }
        });
        
        // @OG
        
        // select with alt + click
        
        $('#result_list tbody tr').click(function(e){
          if (e.altKey) {
            if (e.target.className != 'action-select') {
              var checkbox = $(this).find('.action-select');
              checkbox.prop('checked', checkbox.is(':checked') ? false : true);
              $(this).toggleClass(options.selectedClass, checkbox.is(':checked'));
              updateCounter();
              return false;
            } 
          }
        });
    
        // actions
      
        var actions = $('<menu />', {label: "Akcja"});
      
        $('#changelist-form select[name=action] option').each(function() {
          var option = $(this); 
          if (option.attr('value')) {
            var menuitem = $("<menuitem />", {label: option.text().trim()});
            menuitem.on("click", function(e) {
              if ($('.action-select').filter(":checked").length) {
                $('#changelist-form select').val(option.attr('value'));
                $('#changelist-form').submit();
              } else {
                alert('Wykonanie akcji wymaga wybrania obiektów. Żaden obiekt nie został zmieniony.');
              }
            });
            menuitem.appendTo(actions);
          }
        });
        
        // tools
        
        var tools = $('<menu />', {label: "Dodatkowe opcje"});
        
        $('ul.object-tools a').each(function() {
          var anchor = $(this);
          var menuitem = $("<menuitem />", {label: anchor.text().trim()});
          menuitem.on("click", function(e) {
            location.href = anchor.attr('href');
          });
          menuitem.appendTo(tools);
        });
        
        // contextmenu
        
        var actions_length = $('menuitem', actions).length;
        var tools_length = $('menuitem', tools).length;
        
        if (actions_length || tools_length) {
          var contextmenu = $('<menu />', {id: "contextmenu", type: "context"});
          if (actions_length) contextmenu.append(actions);
          if (tools_length) contextmenu.append(tools);
          $('body').append(contextmenu).attr('contextmenu', 'contextmenu');
        }    
        
    };
    
    /* Setup plugin defaults */
    $.fn.actions.defaults = {
        actionContainer: "div.actions",
        counterContainer: "span.action-counter",
        allContainer: "div.actions span.all",
        acrossInput: "div.actions input.select-across",
        acrossQuestions: "div.actions span.question",
        acrossClears: "div.actions span.clear",
        allToggle: "#action-toggle",
        selectedClass: "selected"
    };
    $(document).ready(function() {
        var $actionsEls = $('tr input.action-select');
        if ($actionsEls.length > 0) {
            $actionsEls.actions();
        }
    });
})(django.jQuery);
