
/* ------------------------------------------------------------------------------
    T E Y L E R S
--------------------------------------------------------------------------------- */
(function($)
{
    /**
     * Auto-growing textareas; technique ripped from Facebook
     * 
     * 
     * http://github.com/jaz303/jquery-grab-bag/tree/master/javascripts/jquery.autogrow-textarea.js
     */
    $.fn.autogrow = function(options)
    {
        return this.filter('textarea').each(function()
        {
            var self         = this;
            var $self        = $(self);
            var minHeight    = $self.height();
            var noFlickerPad = $self.hasClass('autogrow-short') ? 0 : parseInt($self.css('lineHeight')) || 0;
            var settings = $.extend({
                preGrowCallback: null,
                postGrowCallback: null
              }, options );

            var shadow = $('<div></div>').css({
                position:    'absolute',
                top:         -10000,
                left:        -10000,
                width:       $self.width(),
                fontSize:    $self.css('fontSize'),
                fontFamily:  $self.css('fontFamily'),
                fontWeight:  $self.css('fontWeight'),
                lineHeight:  $self.css('lineHeight'),
                resize:      'none',
                'word-wrap': 'break-word'
            }).appendTo(document.body);

            var update = function(event)
            {
                var times = function(string, number)
                {
                    for (var i=0, r=''; i<number; i++) r += string;
                    return r;
                };

                var val = self.value.replace(/&/g, '&amp;')
                                    .replace(/</g, '&lt;')
                                    .replace(/>/g, '&gt;')
                                    .replace(/\n$/, '<br/>&nbsp;')
                                    .replace(/\n/g, '<br/>')
                                    .replace(/ {2,}/g, function(space){ return times('&nbsp;', space.length - 1) + ' ' });

                // Did enter get pressed?  Resize in this keydown event so that the flicker doesn't occur.
                if (event && event.data && event.data.event === 'keydown' && event.keyCode === 13) {
                    val += '<br />';
                }

                shadow.css('width', $self.width());
                shadow.html(val + (noFlickerPad === 0 ? '...' : '')); // Append '...' to resize pre-emptively.
                
                var newHeight=Math.max(shadow.height() + noFlickerPad - 20, minHeight);
                if(settings.preGrowCallback!=null){
                  newHeight=settings.preGrowCallback($self,shadow,newHeight,minHeight);
                }
                
                $self.height(newHeight);
                
                if(settings.postGrowCallback!=null){
                  settings.postGrowCallback($self);
                }
            }

            $self.change(update).keyup(update).keydown({event:'keydown'},update);
            $(window).resize(update);

            update();
        });
    };
})(jQuery);

$(document).ready(function() {
    /* AUTOCOMPLETE WIDGET */

    $("body.template-edit fieldset:not(#fieldset-default) textarea").autogrow();

    function hideSelectQuerySearch(autocompleteDiv) {
        if (autocompleteDiv.find("span.option").length > 0) {
          $(autocompleteDiv.find("div.querySelectSearch")).addClass('hidden'); 
        }
    }

    function unselectSelectedOptions(parent, item) {
        var options = parent.find('span.option input.contenttree-widget:not(.isSelected)');
        options.each(function() {
            span = $(this).closest('span.option');
            span.remove()
            /*if (!span.hasClass("hidden")) {
                span.addClass("hidden");
            }*/
        });
    }

    function optionChangeAction(item) {
        if (item.is(":checked") == false) {
            $parent = $(item.closest("div[id$='autocomplete']"));
            $querySelector = $parent.find('div.querySelectSearch')
                if ($querySelector.hasClass('hidden')) {
                $querySelector.removeClass('hidden')
            }

            if (item.hasClass("isSelected")) {
                item.removeClass("isSelected");
            }

        } else {
            $parent = $(item.closest("div[id$='autocomplete']"));

            if (!item.hasClass("isSelected")) {
                item.addClass("isSelected");
            }
            unselectSelectedOptions($parent, item);

            $querySelector = $parent.find('div.querySelectSearch')
            if (!$querySelector.hasClass('hidden')) {
                $querySelector.addClass('hidden')
            }
        }
    }

    /* Do not show search box if there's any option selected */
    $("div[id$='autocomplete']").each(function() {
        $autocompleteDiv = $(this);
        hideSelectQuerySearch($autocompleteDiv);
    });

    /* Action when item is added */
    $('div.autocompleteInputWidget').each(function() {
        $(this).bind("DOMSubtreeModified", function() {

            $divParent = $($(this).closest("div[id$='autocomplete']"));
            hideSelectQuerySearch($divParent);

            /* Generate change actions for new options */
            $(this).find('input.contenttree-widget').change(function() {
                optionChangeAction($(this));
            });
        });
    });

    /* Action when options is selected/unselected */
    $("input.contenttree-widget").change(function() {
        optionChangeAction($(this));
    });

});

