
/* ------------------------------------------------------------------------------
    C U S T O M
--------------------------------------------------------------------------------- */

$(document).ready(function() {
    /* AUTOCOMPLETE WIDGET */
    
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

