ckan.module('projection-autocomplete', function(jQuery, _) {
    return {

        options: {
            search_epsg_url: null,
            layer_idx: null,
        },
        initialize: function() {
            var module = this;
            var autocomplete_el = $("#layer_srs_" + this.options.layer_idx)
                .autocomplete({
                    source: module.options.search_epsg_url,
                    minLength: 3,
                    select: function(event, ui) {
                        autocomplete_el.val(ui.item.label);
                    }
                });
        },
    };

});