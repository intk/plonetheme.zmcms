
/* ------------------------------------------------------------------------------
    C U S T O M
--------------------------------------------------------------------------------- */


$(document).ready(function() {
    
    // Disable inputs in private view
    $("div.template-edit input, div.template-edit select:not(.formTabs), div.template-edit textarea, div.template-edit button").prop("disabled", true);

    $("body.template-edit select.formTabs").change(function() {
        var select_element = $(this);
        var option_selected = $(this).find("option:selected");
        var fieldsetlegend_id = option_selected.attr("id");
        var fieldset_id = fieldsetlegend_id.replace("fieldsetlegend-", "");
        
        if (fieldset_id != "default") {
            var query = "?fieldset=" + fieldset_id + "&ajax_load=true";
            var link = window.location.href;
            url = link + query

            var original_fieldset = $("fieldset#fieldset-"+fieldset_id);
            original_fieldset.show();

            $.ajax({
                url: url,
                success: function(data) {
                    var fieldset = $(data).find("fieldset#fieldset-"+fieldset_id);
                    var original_fieldset = $("fieldset#fieldset-"+fieldset_id);
                    fieldset.find('legend').remove();
                    original_fieldset.html(fieldset.html());
                    $(document).trigger('readyAgain');
                    original_fieldset.show();
                }
            });
        }


    });
});



