
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
    $("table.datagridwidget-table-view input.contenttree-widget").change(function() {
        optionChangeAction($(this));
    });

});

function formwidget_autocomplete_ready(event, data, formatted) {
    (function($) { 
        var input_box = $(event.target);
        html = data[1];
        var no_lt = html.replace(/&lt;/g, "<");
        var res = no_lt.replace(/&gt;/g, ">");
        var new_data = res;

        formwidget_autocomplete_new_value(input_box,data[0],new_data);
    }(jQuery));
}

function formwidget_autocomplete_new_value(input_box,value,label) {
    (function($) { 
        var base_id = input_box[0].id.replace(/-widgets-query$/,"");
        var base_name = input_box[0].name.replace(/\.widgets\.query$/,"");
        var widget_base = $('#'+base_id+"-input-fields");

        var all_fields = widget_base.find('input:radio, input:checkbox');
        
        // Clear query box and uncheck any radio boxes
        input_box.val("");
        widget_base.find('input:radio').prop('checked', false);
        
        // If a radio/check box for this value already exists, check it.
        var selected_field = widget_base.find('input[value="' + value + '"]');
        if(selected_field.length) {
            selected_field.each(function() { this.checked = true; });
            return;
        }

        widget_base, base_name, base_id
        // Create the box for this value
        var idx = all_fields.length;
        var klass = widget_base.data('klass');
        var title = widget_base.data('title');
        var type = widget_base.data('input_type');
        var multiple = widget_base.data('multiple');
        var span = $('<span/>').attr("id",base_id+"-"+idx+"-wrapper").attr("class","option");
        // Note that Internet Explorer will usually *not* let you set the name via setAttribute.
        // Also, setting the type after adding a input to the DOM is also not allowed.
        // Last but not least, the checked attribute doesn't always behave in a way you'd expect
        // so we generate this one as text as well.
        span.append($("<label/>").attr("for",base_id+"-"+idx)
                                 .append($('<input type="' + type + '"' +
                                                ' name="' + base_name + (multiple?':list"':'"') +
                                                ' checked="checked" />')
                                            .attr("id",base_id+"-"+idx)
                                            .attr("title",title)
                                            .attr("value",value)
                                            .addClass(klass)
                                        )
                                 .append(" ")
                                 .append($("<span>").attr("class","label").html(label))
                                 );
        widget_base.append(span);
    }(jQuery));
}

