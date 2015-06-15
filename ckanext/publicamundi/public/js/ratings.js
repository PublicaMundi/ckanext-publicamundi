"use strict"; 

ckan.module('dataset-rating', function($, _) {
    return {
        initialize: function() {
            var console = window.console;
            var debug = $.proxy(console, 'debug');
            $.proxyAll(this, /_on/);

            this.el.on('click', this._onClick);
            
        },
        _onClick: function(event) {
            var rating = this.options.rating;
            var name = this.options.pkg_name;
            var res = this.sandbox.client.call('POST', 'rating_create', {'package':name, 'rating':rating} , function(json) { 
                if (json.success == true){
                    $('#rating-count').text(json.result['rating count']);
                    $('#rating-average').text(json.result['rating average']);
                    location.reload();
                }

            });
            
            
        },
}
});
