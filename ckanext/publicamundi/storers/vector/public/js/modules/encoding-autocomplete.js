ckan.module('encoding-autocomplete', function(jQuery, _) {
    return {

        options: {
            search_encoding_url: null,
            layer_idx: null,
        },
        initialize: function() {

            var module = this;
            var autocomplete_el = $("#layer_encoding_" + this.options.layer_idx)
                .autocomplete({
                    source: module.options.search_encoding_url,
                    minLength: 3,
                    select: function(event, ui) {
                        autocomplete_el.val(ui.item.label);
                    }
                });
        },
    };

});