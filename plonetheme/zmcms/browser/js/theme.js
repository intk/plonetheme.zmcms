
/* ------------------------------------------------------------------------------
    C U S T O M
--------------------------------------------------------------------------------- */
(function(history){
    var replaceState = history.replaceState;
    history.replaceState = function(state, title, url) {
        if (typeof history.onpushstate == "function") {
            history.onpushstate({state: state, url: url});
        }
        // whatever else you want to do
        // maybe call onhashchange e.handler
        return replaceState.apply(history, arguments);
    }
})(window.history);

var createRelatedItemsLink = function(elem) {
    setTimeout(function() {
        all_relateditems = $(elem+' span.pattern-relateditems-item');
        all_relateditems.each(function() {
            var title_elem = $(this).find("span.pattern-relateditems-item-title");
            var link_elem = $(this).find("span.pattern-relateditems-item-path");
            var title = title_elem.html();
            var link = link_elem.html();

            var new_link = $("<a></a>").attr("href", link).html(title);
            title_elem.html(new_link);
        });
    }, 3000);
}

var ajaxLoadTabs = function(fieldset_id) {
    $("body.template-edit select.formTabs, div.template-edit select.formTabs").prop("disabled", true);

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
                                //createRelatedItemsLink(real_fieldset_id);
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
                                createRelatedItemsLink(real_fieldset_id);
                            } 
                        }
                    });
                    $("body.template-edit select.formTabs, div.template-edit select.formTabs").prop("disabled", false);
                }
            });
        }
    }
}

var cleanTabs = function() {
    $("fieldset").html('');
}

var getNextTabs = function(fieldset_id, link) {
    $("div.template-edit select.formTabs").prop("disabled", true);

    var query = "/edit?fieldset=" + fieldset_id + "&ajax_load=true";
    var original_link = link;
    var link = link.split("?")[0];

    url = link + query

    $.ajax({
        url: url,
        success: function(data) {
            var fieldsets = $(data).find("fieldset");
            fieldsets.each(function() {
                var _id = $(this).attr("id");
                if (fieldset_id == 'all') {
                    if (_id != 'fieldset-default' && _id != 'fieldset-identification') {
                        var fieldset = $(this);
                        var original_fieldset = $("fieldset#"+_id);
                        fieldset.find('legend').remove();
                        original_fieldset.html(fieldset.html());
                        var real_fieldset_id = "fieldset#"+_id;
                        dataGridField2Functions.init();
                        $(document).trigger('readyAgain', [{fieldset_id: $(real_fieldset_id)}]);
                        $("div.template-edit input, div.template-edit select:not(.formTabs), div.template-edit textarea, div.template-edit button").prop("disabled", true);
                        createRelatedItemsLink(real_fieldset_id);
                    } 
                } else {
                    if (_id != 'fieldset-default') {
                        var fieldset = $(this);
                        var original_fieldset = $("fieldset#"+_id);
                        fieldset.find('legend').remove();
                        original_fieldset.html(fieldset.html());
                        var real_fieldset_id = "fieldset#"+_id;
                        dataGridField2Functions.init();
                        $(document).trigger('readyAgain', [{fieldset_id: $(real_fieldset_id)}]);
                        $("div.template-edit input, div.template-edit select:not(.formTabs), div.template-edit textarea, div.template-edit button").prop("disabled", true);
                        createRelatedItemsLink(real_fieldset_id);
                    }
                }
            });
                
            if (fieldset_id != 'all') {
                $("select.formTabs").val('fieldset-identification').trigger("change");
                getNextTabs('all', original_link);
            } else {
                $("div.template-edit select.formTabs").prop("disabled", false);
            }
        }
    });
}


$(document).ready(function() {
    setTimeout(function() {
        if (!$("body").hasClass("pat-plone-widgets")) {
            $(document).trigger('readyAgain', [{fieldset_id: "body"}]);
        }
        createRelatedItemsLink("#fieldset-identification");
    }, 500);

    $("body.template-edit select.formTabs, div.template-edit select.formTabs").change(function() {
        $("textarea:not(#form-widgets-IBasic-description):not(.mce_editable)").attr("style", "height: 37.8px !important;");
        setTimeout(function(){  
            $("textarea:not(#form-widgets-IBasic-description):not(.mce_editable)").attr("style", "height: 37px !important;");
        }, 100);
    });

    // Disable inputs in private view
    $("div.template-edit input, div.template-edit select:not(.formTabs), div.template-edit textarea, div.template-edit button").prop("disabled", true);
    ajaxLoadTabs("all");

    if ($("div.template-edit").length > 0) {
        history.onpushstate = function(e) {
            cleanTabs();
            getNextTabs('identification', e.url);
        };
    }
});
