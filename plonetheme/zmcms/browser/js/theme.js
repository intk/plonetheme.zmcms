
/* ------------------------------------------------------------------------------
    C U S T O M
--------------------------------------------------------------------------------- */


var ajaxLoadTabs = function(fieldset_id) {
    $("body.template-edit select.formTabs").prop("disabled", true);

    if ($("body").hasClass("template-edit")) {

        if (fieldset_id != "default") {
            var query = "?fieldset=" + fieldset_id + "&ajax_load=true";
            var link = window.location.href;
            url = link + query

            $.ajax({
                url: url,
                success: function(data) {
                    var fieldsets = $(data).find("fieldset");
                    fieldsets.each(function() {
                        var _id = $(this).attr("id");
                        if (_id != 'fieldset-default') {
                            var fieldset = $(this);
                            var original_fieldset = $("fieldset#"+_id);
                            fieldset.find('legend').remove();
                            original_fieldset.html(fieldset.html());
                            var real_fieldset_id = "#"+_id;
                            $(document).trigger('readyAgain', [{fieldset_id: real_fieldset_id}]);
                        } 
                    });
                    $(document).trigger('readyAgain', [{fieldset_id: "#fieldset-default"}]);
                    $("body.template-edit select.formTabs").prop("disabled", false);
                    dataGridField2Functions.init();
                }
            });
        }


    }
}

$(document).ready(function() {
    // Disable inputs in private view
    $("div.template-edit input, div.template-edit select:not(.formTabs), div.template-edit textarea, div.template-edit button").prop("disabled", true);
    ajaxLoadTabs("all");
    //console.log($("#fieldset-default").find(".mce-container").length);
    if ($("#fieldset-default .mce-container").length <= 0) {
        $(document).trigger('readyAgain', [{fieldset_id: "#fieldset-default"}]);
    }
});
