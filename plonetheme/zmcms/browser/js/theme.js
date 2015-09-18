
/* ------------------------------------------------------------------------------
    C U S T O M
--------------------------------------------------------------------------------- */


var ajaxLoadTabs = function(fieldset_id) {
    $("body.template-edit select.formTabs, div.template-edit select.formTabs").prop("disabled", true);

    $("body.template-edit select.formTabs, div.template-edit select.formTabs").change(function() {
        $("textarea").attr("style", "height: 37.8px !important;");
        setTimeout(function(){  
            $("textarea").attr("style", "height: 37px !important;");
        }, 100);
    });

    if ($("body").hasClass("template-edit") || $("body div.template-edit").length > 0) {

        if (fieldset_id != "default") {
            if ($("body").hasClass("template-edit")) {
                var query = "?fieldset=" + fieldset_id + "&ajax_load=true";
            } else {
                var query = "/edit?fieldset=" + fieldset_id + "&ajax_load=true";
            }

            var link = window.location.href;
            if (window.location.search != "") {
                link = window.location.protocol + "//" + window.location.host + window.location.pathname;
            } 

            url = link + query

            $.ajax({
                url: url,
                success: function(data) {
                    var fieldsets = $(data).find("fieldset");
                    fieldsets.each(function() {
                        var _id = $(this).attr("id");
                        if ($("body").hasClass("template-edit")) {
                            if (_id != 'fieldset-default') {
                                var fieldset = $(this);
                                var original_fieldset = $("fieldset#"+_id);
                                fieldset.find('legend').remove();
                                original_fieldset.html(fieldset.html());
                                var real_fieldset_id = "fieldset#"+_id;
                                dataGridField2Functions.init();
                                $(document).trigger('readyAgain', [{fieldset_id: $(real_fieldset_id)}]);
                            } 
                        } else {
                            if (_id != 'fieldset-default' && _id != 'fieldset-identification') {
                                var fieldset = $(this);
                                var original_fieldset = $("fieldset#"+_id);
                                fieldset.find('legend').remove();
                                original_fieldset.html(fieldset.html());
                                var real_fieldset_id = "fieldset#"+_id;
                                dataGridField2Functions.init();
                                $(document).trigger('readyAgain', [{fieldset_id: $(real_fieldset_id)}]);
                                $("div.template-edit input, div.template-edit select:not(.formTabs), div.template-edit textarea, div.template-edit button").prop("disabled", true);
                            } 
                        }
                    });
                    $("body.template-edit select.formTabs, div.template-edit select.formTabs").prop("disabled", false);
                }
            });
        }


    }
}

$(document).ready(function() {
    setTimeout(function() {
        if (!$("body").hasClass("pat-plone-widgets")) {
            $(document).trigger('readyAgain', [{fieldset_id: "body"}]);
        }
    }, 500);

    // Disable inputs in private view
    $("div.template-edit input, div.template-edit select:not(.formTabs), div.template-edit textarea, div.template-edit button").prop("disabled", true);
    ajaxLoadTabs("all");
});
