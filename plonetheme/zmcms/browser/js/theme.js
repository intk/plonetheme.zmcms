
/* ------------------------------------------------------------------------------
    C U S T O M
--------------------------------------------------------------------------------- */

var SELECT_TAB_QUERY = "body.template-edit.portaltype-object select.formTabs, body:not(.template-edit) div.template-edit select.formTabs"
var INPUTS_QUERY = "div.template-edit input, div.template-edit select:not(.formTabs), div.template-edit textarea, div.template-edit button"

var fix_textareas = function() {
    $("textarea:not(#form-widgets-IBasic-description):not(.mce_editable)").attr("style", "height: 37.8px !important;");
    setTimeout(function(){  
        $("textarea:not(#form-widgets-IBasic-description):not(.mce_editable)").attr("style", "height: 37px !important;");
    }, 100);
};

var disable_inputs = function() {
    $(INPUTS_QUERY).prop("disabled", true);
};

var enable_inputs = function() {
    $(INPUTS_QUERY).prop("disabled", false);
}

var disable_selecttab = function() {
    $("select.formTabs").prop("disabled", true);
};

var enable_selecttab = function() {
    $("select.formTabs").removeAttr("disabled");
};

var show_ajax_error = function(textStatus, errorThrown) {
    var message = "<span>Status: "+textStatus+"<br>Message: "+errorThrown+"</span>"
    $("#ajax-error-msg").html(message);
    $("#ajax-error-msg").show();
};

var in_allowed_portaltypes = function() {
    if ($("body").hasClass("portaltype-object") || $("body").hasClass("portaltype-book") || $("body").hasClass("portaltype-image") || $("body").hasClass('portaltype-personorinstitution') || $("body").hasClass('portaltype-exhibition') || $("body").hasClass('portaltype-audiovisual') || $("body").hasClass('portaltype-treatment') || $("body").hasClass('portaltype-outgoingloan') || $("body").hasClass("portaltype-incomingloan") || $("body").hasClass("portaltype-objectentry") || $("body").hasClass("portaltype-resource") || $("body").hasClass("portaltype-taxonomie") || $("body").hasClass("portaltype-serial") || $("body").hasClass("portaltype-article")) {
        return true;
    }
    return false;
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


var click_on_generated_link = function(obj) {
    var href = obj.getAttribute("href");
    window.location.href = window.location.protocol + "//" + window.location.host + href;
}

var createRelatedItemsLink = function(elem, timeout, shot) {
    var shot = typeof shot !== 'undefined' ? shot : 1;

    setTimeout(function() {
        all_relateditems = $(elem+' div.pattern-relateditems-container');
        
        if ((all_relateditems.length) > 0) {
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
        } else {
            if ($(elem+' div.relationlist-field').length > 0) {
                if (shot < 4) {
                    shot = shot + 1;
                    createRelatedItemsLink(elem, timeout, shot);
                } else {
                    show_ajax_error("Error", "Cannot create relation links for tab: "+elem);
                }
            }
        }

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
            if (last_member == "view" || last_member == "view/" || last_member == "contents_view" || last_member == "contents_view/") {
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
                            } else if ($("body").hasClass('portaltype-personorinstitution')) {
                                if (_id != 'fieldset-default' && _id != 'fieldset-name_information') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 
                            } else if ($("body").hasClass('portaltype-exhibition')) {
                                if (_id != 'fieldset-default' && _id != 'fieldset-exhibitions_details') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 
                            } else if ($("body").hasClass('portaltype-book') || $("body").hasClass('portaltype-audiovisual') || $("body").hasClass('portaltype-serial') || $("body").hasClass("portaltype-article")) {
                                if (_id != 'fieldset-default' && _id != 'fieldset-title_author') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 
                            } else if ($("body").hasClass('portaltype-treatment')) {
                                if (_id != 'fieldset-default' && _id != 'fieldset-treatment_details') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 
                            } else if ($("body").hasClass('portaltype-outgoingloan') || $("body").hasClass("portaltype-incomingloan")) {
                                if (_id != 'fieldset-default' && _id != 'fieldset-loan_request') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 
                            } else if ($("body").hasClass('portaltype-objectentry')) {
                                if (_id != 'fieldset-default' && _id != 'fieldset-general') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 
                            } else if ($("body").hasClass('portaltype-resource')) {
                                if (_id != 'fieldset-default' && _id != 'fieldset-resource_dublin_core') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 
                            } else if ($("body").hasClass('portaltype-taxonomie')) {
                                if (_id != 'fieldset-default' && _id != 'fieldset-taxonomic_term_details') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 

                            } else if ($("body").hasClass('portaltype-image')) {
                                if (_id != 'fieldset-default' && _id != 'fieldset-reproduction_data') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 
                            } else {
                                if (_id != 'fieldset-default' && _id != 'fieldset-identification') {
                                    var fieldset = $(this);
                                    var original_fieldset = $("fieldset#"+_id);
                                    original_fieldset.html(fieldset.html());
                                } 
                            }
                        });

                        // Disable inputs
                        disable_inputs();
                        
                        /* Init datagrid */
                        if ($("body").hasClass("template-edit")) {
                            //dataGridField2Functions.init();
                            create_taxonomic_events();
                        }
                    }, 50);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    if (errorThrown == "") {
                        errorThrown = "Unable to get tabs. Please <a href='"+window.location.href+"'>refresh</a> the page."
                    } else {
                        errorThrown = errorThrown + " - Unable to get tabs."
                    }
                    show_ajax_error(textStatus, errorThrown);
                }
            });

        }
    }
};

// EVENTS

var change_tab_event = function(tab) {
    if ($("body").hasClass("template-edit")) {
        var data_id = tab.val().replace("fieldsetlegend-", "");
        var element = $("fieldset#fieldset-"+data_id);
        
        if (!element.hasClass('widgets-init') && data_id != "default") {
            init_datagrid(element);
            init_widgets(element);
            
            var relateditems_elements = element.find('input.pat-relateditems');
            if (relateditems_elements.length) {
                related_input = relateditems_elements[0];
                var select_container = $(related_input).data();
                var patternRelateditems = select_container.patternRelateditems;
                if (patternRelateditems == undefined) {
                    errorThrown = "Interface was not properly initialised. Please <a href='"+window.location.href+"'>refresh</a> the page."
                    show_ajax_error("Warning", errorThrown);
                }
            } 
            element.addClass('widgets-init');
        }
        //fix_textareas();
        fix_textareas_height("fieldset#fieldset-"+data_id);

    } else if ($("body").hasClass("portaltype-book") || $("body").hasClass("portaltype-audiovisual") || $("body").hasClass('portaltype-serial') || $("body").hasClass("portaltype-article")) {
        var data_id = tab.val();
        var element = $("fieldset#"+data_id);
        fix_textareas_height("fieldset#"+data_id);

        if (!element.hasClass('widgets-init') && data_id != "fieldset-title_author") {
            init_datagrid(element);
            init_widgets(element);
            element.addClass('widgets-init');
        }
    } else if ($("body").hasClass("portaltype-personorinstitution")) {
        var data_id = tab.val();
        var element = $("fieldset#"+data_id);
        fix_textareas_height("fieldset#"+data_id);

        if (!element.hasClass('widgets-init') && data_id != "fieldset-name_information") {
            init_datagrid(element);
            init_widgets(element);
            element.addClass('widgets-init');
        }
    } else if ($("body").hasClass("portaltype-exhibition")) {
        var data_id = tab.val();
        var element = $("fieldset#"+data_id);
        fix_textareas_height("fieldset#"+data_id);

        if (!element.hasClass('widgets-init') && data_id != "fieldset-exhibitions_details") {
            init_datagrid(element);
            init_widgets(element);
            element.addClass('widgets-init');
        }
    } else if ($("body").hasClass("portaltype-treatment")) {
        var data_id = tab.val();
        var element = $("fieldset#"+data_id);
        fix_textareas_height("fieldset#"+data_id);

        if (!element.hasClass('widgets-init') && data_id != "fieldset-treatment_details") {
            init_datagrid(element);
            init_widgets(element);
            element.addClass('widgets-init');
        }
    } else if ($("body").hasClass("portaltype-outgoingloan") || $("body").hasClass("portaltype-incomingloan")) {
        var data_id = tab.val();
        var element = $("fieldset#"+data_id);
        fix_textareas_height("fieldset#"+data_id);

        if (!element.hasClass('widgets-init') && data_id != "fieldset-loan_request") {
            init_datagrid(element);
            init_widgets(element);
            element.addClass('widgets-init');
        }
    } else if ($("body").hasClass("portaltype-objectentry")) {
        var data_id = tab.val();
        var element = $("fieldset#"+data_id);
        fix_textareas_height("fieldset#"+data_id);

        if (!element.hasClass('widgets-init') && data_id != "fieldset-general") {
            init_datagrid(element);
            init_widgets(element);
            element.addClass('widgets-init');
        }
    } else if ($("body").hasClass("portaltype-resource")) {
        var data_id = tab.val();
        var element = $("fieldset#"+data_id);
        

        if (!element.hasClass('widgets-init') && data_id != "fieldset-resource_dublin_core") {
            init_datagrid(element);
            init_widgets(element);
            element.addClass('widgets-init');
        }

        fix_textareas_height("fieldset#"+data_id);
    } else if ($("body").hasClass("portaltype-image")) {
        var data_id = tab.val();
        var element = $("fieldset#"+data_id);
        

        if (!element.hasClass('widgets-init') && data_id != "fieldset-reproduction_data") {
            init_datagrid(element);
            init_widgets(element);
            element.addClass('widgets-init');
        }

        fix_textareas_height("fieldset#"+data_id);
    } else {
        var data_id = tab.val();
        var element = $("fieldset#"+data_id);
        
        if (!element.hasClass('widgets-init') && data_id != "fieldset-identification") {
            init_datagrid(element);
            init_widgets(element);
            element.addClass('widgets-init');
        }

        fix_textareas_height("fieldset#"+data_id);
    }
}

var initiate_first_tab = function(timeout) {
    setTimeout(function() {
        if (!$("body").hasClass("pat-plone-widgets")) {
            if ($("body").hasClass('template-edit')) {
                init_widgets($('body'));
                fix_textareas_height("body");
            } else {
                return true;
                if ($("body").hasClass("portaltype-object")) {
                    init_widgets($("fieldset#fieldset-identification"));
                } else if ($("body").hasClass("portaltype-book") || $("body").hasClass("portaltype-audiovisual") || $("body").hasClass('portaltype-serial') || $("body").hasClass("portaltype-article")) {
                    init_widgets($("fieldset#fieldset-title_author"));
                } else if ($("body").hasClass("portaltype-personorinstitution")) {
                    init_widgets($("fieldset#fieldset-name_information"));
                } else if ($("body").hasClass("portaltype-exhibition")) {
                    init_widgets($("fieldset#fieldset-exhibitions_details"));
                } else if ($("body").hasClass("portaltype-treatment")) {
                    init_widgets($("fieldset#fieldset-treatment_details"));
                } else if ($("body").hasClass("portaltype-outgoingloan") || $("body").hasClass("portaltype-incomingloan")) {
                    init_widgets($("fieldset#fieldset-loan_request"));
                } else if ($("body").hasClass("portaltype-objectentry")) {
                    init_widgets($("fieldset#fieldset-general"));
                } else if ($("body").hasClass("portaltype-resource")) {
                    init_widgets($("fieldset#fieldset-resource_dublin_core"));
                } else if ($("body").hasClass("portaltype-taxonomie")) {
                    init_widgets($("fieldset#fieldset-taxonomic_term_details"));
                } else if ($("body").hasClass("portaltype-image")) {
                    init_widgets($("fieldset#fieldset-reproduction_data"));
                }
            }
        } else {
            // Widgets already created
        }
    }, timeout);
}

// Set plone form max tabs
ploneFormTabbing.max_tabs = 0;


var change_taxonomic_query = function(option) {
    var rank_value = option.val();

    var parent = $(option).parents('.datagridwidget-block-edit-cell');
    var related_input = parent.find('input.pat-relateditems');
    var select_container = $(related_input).data();

    var patternRelateditems = select_container.patternRelateditems;
    var criterias = select_container.patternRelateditems.query.getCriterias();
    var attributes = select_container.patternRelateditems.options.attributes;

    $(related_input).val('');
    parent.find('.pattern-relateditems-container li.select2-search-choice').remove();

    select_container.select2.opts.ajax.data = function(term, page) {
        var data = {
            query: JSON.stringify({
              criteria: criterias,
              taxonomic_rank: rank_value
            }),
            attributes: JSON.stringify(attributes),
        };
        if (page) {
            data.batch = JSON.stringify(patternRelateditems.query.getBatch(page));
        }
        return data;
    };
}

var create_taxonomic_events = function() {
    $("#formfield-form-widgets-identification_taxonomy .datagridwidget-widget-rank select").change(function() {
        change_taxonomic_query($(this));
    });

    $("#formfield-form-widgets-iconography_contentSubjects .datagridwidget-widget-taxonomicRank select").change(function() {
        change_taxonomic_query($(this));
    });

    $("#formfield-form-widgets-associations_associatedSubjects .datagridwidget-widget-taxonomicRank select").change(function() {
        change_taxonomic_query($(this));
    });
}

var fix_textareas_height = function(elem) {
    var textareas = $(elem+" textarea");
    textareas.each(function() {
        if (!$(this).hasClass("mce_editable")) {
            $(this).attr("style", "height:1px;");
            var height = $(this)[0].scrollHeight;

            if (height != 0) {
                if (height == 38) {
                    height = 37;
                }
                
                if (height != 37) {
                    height = height + 3;
                    $(this).attr("style", "height: "+height+"px;");
                } else {
                    $(this).attr("style", "height: "+height+"px;");
                }
            } else {
                $(this).attr("style", "height:37px;");
            }
        }
    });
}

$(document).ready(function() {

    if (in_allowed_portaltypes()) {
        //initiate_first_tab(500)
        setTimeout(function() {
            if (($("body:not(.template-edit) div.template-edit").length > 0) && !$("body").hasClass("pat-plone-widgets")) {
                init_widgets($("body"));
            }
        }, 1000);
    }

    if ($("body").hasClass("template-edit")) {
        $(SELECT_TAB_QUERY).change(function() {
            change_tab_event($(this));
        });
    }

    // Load all tabs
    if ($("body").hasClass("portaltype-object") || ($("body:not(.template-edit) div.template-edit").length > 0)) {
        
        if (!$("body").hasClass("template-edit")) {
            disable_inputs();
            setTimeout(function() {
                fix_textareas_height("body");
            }, 600);   
        } 

        if ($("body").hasClass("template-edit")) {
            disable_selecttab();
            ajaxLoadTabs("all");
        }
    } else {

    }
    
    // NEEDS FIX
    if ($("body").hasClass("template-collective-taxonomie-taxonomie") || $("body[class^='template-collective-']").length > 0 || $("body.template-edit.portaltype-collection").length > 0 || $("body").hasClass("template-collection")) {
        setTimeout(function() {
            if (!$("body").hasClass("pat-plone-widgets")) {
                init_widgets($("body"));
            }
        }, 1000);
    }

    if (!$("body").hasClass('template-edit')) {
        create_taxonomic_events();
    }
});

