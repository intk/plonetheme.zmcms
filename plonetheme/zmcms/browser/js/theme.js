
/* ------------------------------------------------------------------------------
    C U S T O M
--------------------------------------------------------------------------------- */
var fix_textareas = function() {
    $("textarea:not(#form-widgets-IBasic-description):not(.mce_editable)").attr("style", "height: 37.8px !important;");
    setTimeout(function(){  
        $("textarea:not(#form-widgets-IBasic-description):not(.mce_editable)").attr("style", "height: 37px !important;");
    }, 100);
};

var disable_inputs = function() {
    $("div.template-edit input, div.template-edit select:not(.formTabs), div.template-edit textarea, div.template-edit button").prop("disabled", true);
};

var enable_inputs = function() {
    $("div.template-edit input, div.template-edit select:not(.formTabs), div.template-edit textarea, div.template-edit button").prop("disabled", false);
}

var disable_selecttab = function() {
    $("select.formTabs").prop("disabled", true);
};

var enable_selecttab = function() {
    $("select.formTabs").removeAttr("disabled");
};

var show_ajax_error = function(textStatus, errorThrown) {
    var message = "<span>Status: "+textStatus+"<br>Error: "+errorThrown+"</span>"
    $("#ajax-error-msg").html(message);
    $("#ajax-error-msg").show();
};

(function(history){
    var replaceState = history.replaceState;
    history.replaceState = function(state, title, url) {
        if (typeof history.onpushstate == "function") {
            history.onpushstate({state: state, url: url});
        }
        return replaceState.apply(history, arguments);
    }
})(window.history);

var createRelatedItemsLink = function(elem, timeout) {
    setTimeout(function() {
        all_relateditems = $(elem+' span.pattern-relateditems-item');
        all_relateditems.each(function() {
            var title_elem = $(this).find("span.pattern-relateditems-item-title");
            var link_elem = $(this).find("span.pattern-relateditems-item-path");
            var title = title_elem.html();
            var link = link_elem.html();

            var new_link = $("<a></a>").attr("href", link).html(title);
            new_link.click(function() {
                window.location.href = window.location.protocol + "//" + window.location.host + $(this).attr("href");
            });
            title_elem.html(new_link);
        });
    }, timeout);
};

var init_widgets = function(data_id) {
    var element = data_id;
    $(document).trigger('readyAgain', [{fieldset_id: element}]);
};

var init_datagrid = function(element) {
    element.find('.datagridwidget-body').each(function() {
        var $this = $(this);
        
        aa = $this.children(".auto-append").size() > 0;
        $this.data("auto-append", aa);

        // Hint CSS
        if (aa) {
            $this.addClass("datagridwidget-body-auto-append");
        } else {
            $this.addClass("datagridwidget-body-non-auto-append");
        }

        dataGridField2Functions.updateOrderIndex(this, false);

        if (!aa) {
            dataGridField2Functions.ensureMinimumRows(this);
        }
    }); 
}

var ajaxLoadTabs = function(fieldset_id) {
    if ($("body").hasClass("template-edit") || $("body div.template-edit").length > 0) {
        if (fieldset_id != "default") {
            if ($("body").hasClass("template-edit")) {
                var query = "?fieldset=" + fieldset_id + "&ajax_load=true";
            } else {
                var query = "/edit?fieldset=" + fieldset_id + "&ajax_load=true";
            }

            var link = window.location.href;
            if (window.location.search != "" || window.location.hash != "") {
                link = window.location.protocol + "//" + window.location.host + window.location.pathname;
                
            } 

            link_split = link.split('/');
            last_member = link_split[link_split.length-1]
            if (last_member == "view" || last_member == "view/") {
                link_split[link_split.length-1] = "";
                link = link_split.join('/');
            }

            url = link + query;

            $.ajax({
                url: url,
                success: function(data) {
                    // Enable select tab
                    enable_selecttab();

                    setTimeout(function() {
                        var fieldsets = $(data).find("fieldset");
                        fieldsets.each(function() {
                            var _id = $(this).attr("id");

                            if ($("body").hasClass("template-edit")) {
                                if (_id != 'fieldset-default') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 
                            }
                            else if ($("body").hasClass('portaltype-book')) {
                                if (_id != 'fieldset-default' && _id != 'fieldset-title_author') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 
                            }
                            else {
                                if (_id != 'fieldset-default' && _id != 'fieldset-identification') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 
                            }
                        });

                        // Enable inputs
                        disable_inputs();
                        
                        /* Init datagrid */
                        if ($("body").hasClass("template-edit") || $("body").hasClass("portaltype-book")) {
                            dataGridField2Functions.init();
                        }
                    }, 50);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    if (errorThrown == "") {
                        errorThrown = "Unable to get tabs. Please <a href='+"+window.location.href+"+'>refresh</a> the page."
                    } else {
                        errorThrown = errorThrown + " - Unable to get tabs."
                    }
                    show_ajax_error(textStatus, errorThrown);
                }
            });

        }
    }
};

$(document).ready(function() {
    if ($("body").hasClass("portaltype-object") || $("body").hasClass("portaltype-book")) {
        setTimeout(function() {
            if (!$("body").hasClass("pat-plone-widgets")) {
                if ($("body").hasClass('template-edit')) {
                    init_widgets($('body'));
                } else {
                    if ($("body").hasClass("portaltype-object")) {
                        init_widgets($("fieldset#fieldset-identification"));
                        createRelatedItemsLink("fieldset#fieldset-identification", 3000);
                    } else if ($("body").hasClass("portaltype-book")) {
                        init_widgets($("fieldset#fieldset-title_author"));
                        createRelatedItemsLink("fieldset#fieldset-title_author", 3000);
                    }
                }
            } else {
                if ($("body").hasClass("portaltype-object")) {
                    createRelatedItemsLink("fieldset#fieldset-identification", 2000);
                } else if ($("body").hasClass("portaltype-book")) {
                    createRelatedItemsLink("fieldset#fieldset-title_author", 2000);
                }
            }
        }, 900);
    }

    $("body.template-edit.portaltype-object select.formTabs, body:not(.template-edit) div.template-edit select.formTabs").change(function() {
        if ($("body").hasClass("template-edit")) {
            data_id = $(this).val().replace("fieldsetlegend-", "");
            element = $("fieldset#fieldset-"+data_id);
            
            if (!element.hasClass('widgets-init') && data_id != "default") {
                init_widgets(element);
                element.addClass('widgets-init');
            }
            fix_textareas();
        } else if ($("body").hasClass("portaltype-book")) {
            data_id = $(this).val();
            element = $("fieldset#"+data_id);
            
            if (!element.hasClass('widgets-init') && data_id != "fieldset-title_author") {
                init_widgets(element);
                element.addClass('widgets-init');
                createRelatedItemsLink("fieldset#"+data_id, 300);
            }
        } else {
            data_id = $(this).val();
            element = $("fieldset#"+data_id);
            
            if (!element.hasClass('widgets-init') && data_id != "fieldset-identification") {
                init_datagrid(element);
                init_widgets(element);
                element.addClass('widgets-init');
                createRelatedItemsLink("fieldset#"+data_id, 300);
            }
        }
    });

    // Load all tabs
    if ($("body").hasClass("portaltype-object") || ($("body:not(.template-edit) div.template-edit").length > 0)) {
        disable_selecttab();
        if (!$("body").hasClass("template-edit")) {
            disable_inputs(); 
        }
        ajaxLoadTabs("all");
    } else {

    }
});
