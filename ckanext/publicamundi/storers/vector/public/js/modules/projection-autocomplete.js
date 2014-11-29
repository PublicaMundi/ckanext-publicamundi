ckan.module('projection-autocomplete', function(jQuery, _) {
    return {

        options: {
            search_epsg_url:null,
        },
        initialize: function() {
            var module = this;
             
            $("#projection").autocomplete({
                source: module.options.search_epsg_url,
                minLength: 3,
                select: function(event, ui) {
                    $("#projection").val(ui.item.label);
                }
            });
        },
    };

});