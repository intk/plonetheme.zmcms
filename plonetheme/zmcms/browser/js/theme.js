
/* ------------------------------------------------------------------------------
    C U S T O M
--------------------------------------------------------------------------------- */


var ajaxLoadTabs = function(fieldset_id) {
    $("div.template-edit select.formTabs").prop("disabled", true);

    if ($("body").hasClass("template-edit") || $("body div.template-edit").length > 0) {

        if (fieldset_id != "default") {
            if ($("body").hasClass("template-edit")) {
                var query = "?fieldset=" + fieldset_id + "&ajax_load=true";
            } else {
                var query = "/edit?fieldset=" + fieldset_id + "&ajax_load=true";
            }

            var link = window.location.href;
            url = link + query

            $.ajax({
                url: url,
                success: function(data) {
                    var fieldsets = $(data).find("fieldset");
                    fieldsets.each(function() {
                        var _id = $(this).attr("id");
                        if ($("body").hasClass("template-edit")) {
                            if (_id != 'fieldset-default' && _id != 'fieldset-identification' && _id != 'fieldset-production_dating') {
                                var fieldset = $(this);
                                var original_fieldset = $("fieldset#"+_id);
                                fieldset.find('legend').remove();
                                original_fieldset.html(fieldset.html());
                                var real_fieldset_id = "fieldset#"+_id;
                                //$(document).trigger('readyAgain', [{fieldset_id: real_fieldset_id}]);
                            } 
                        } else {
                            if (_id != 'fieldset-default' && _id != 'fieldset-identification') {
                                var fieldset = $(this);
                                var original_fieldset = $("fieldset#"+_id);
                                fieldset.find('legend').remove();
                                original_fieldset.html(fieldset.html());
                                var real_fieldset_id = "fieldset#"+_id;
                                dataGridField2Functions.init();
                                
                                $("div.template-edit input, div.template-edit select:not(.formTabs), div.template-edit textarea, div.template-edit button").prop("disabled", true);
                            } 
                        }
                    });
                    
                    dataGridField2Functions.init();
                    $(document).trigger('readyAgain', [{fieldset_id: "body"}]);

                    $(".tab-spinning").addClass('open');
                    if ($("body").hasClass("template-edit")) {
                        if ($("#fieldset-default .mce-container").length <= 0) {
                            $(document).trigger('readyAgain', [{fieldset_id: "#fieldset-default"}]);
                        }
                    }

                    $("div.template-edit select.formTabs").prop("disabled", false);
                    
                }
            });
        }


    }
}

$(document).ready(function() {
    // Disable inputs in private view
    $("div.template-edit input, div.template-edit select:not(.formTabs), div.template-edit textarea, div.template-edit button").prop("disabled", true);
    ajaxLoadTabs("all");
    if ($("#fieldset-default .mce-container").length <= 0) {
        $(document).trigger('readyAgain', [{fieldset_id: "#fieldset-default"}]);
    }
});
