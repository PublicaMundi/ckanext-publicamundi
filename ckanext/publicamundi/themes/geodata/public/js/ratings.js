"use strict"; 

ckan.module('dataset-rating', function($, _) {
    return {
        initialize: function() {
            var console = window.console;
            var debug = $.proxy(console, 'debug');
            $.proxyAll(this, /_on/);
            
            this.initialize_effect();

            this.el.on('click', this._onClick);
            
        },
        stars : null,
        status: [],
        _onClick: function(event) {
            var rating = this.options.rating;
            var name = this.options.pkg_name;
            var self= this;
            var res = this.sandbox.client.call('POST', 'rating_create', {'package':name, 'rating':rating} , function(json) { 
                if (json.success == true){
                    $('#rating-count').text(json.result['rating count']);
                    $('#rating-average').text(json.result['rating average']);
                    self.update_status();
                }

            });            
        },
        initialize_effect: function() {
            var self = this;
            this.stars = $('.package-rating a');
            this.stars.on('mouseenter', function(event){
                var hover = $(this);
                var hover_val = $(this).data('module-rating');
                self.stars.each(function(idx) {
                    if ($(this).data('module-rating') <= hover_val){
                        var prev = $(this).attr('class');
                        $(this).removeClass(prev);
                        $(this).addClass('icon-star');
                    }
                    else{
                        var prev = $(this).attr('class');
                        $(this).removeClass(prev);
                        $(this).addClass('icon-star-empty');
                    }
                })
            });

            $('.package-rating').on('mouseleave', function(event){
                self.stars.each(function(idx) {
                    var prev = $(this).attr('class');
                    console.log(prev);
                    $(this).removeClass(prev);
                    $(this).addClass(self.status[idx]);
                    //update_status();
                })
            });

            this.update_status();
        },
        update_status: function(){
            var self = this;
            var rating_avg = parseFloat($('#rating-average').text());
            this.stars.each(function(idx){
                var prev = $(this).attr('class');
                $(this).removeClass(prev);
                if ($(this).data('module-rating') <= rating_avg){
                    $(this).addClass('icon-star');
                }
                else if (($(this).data('module-rating') > rating_avg) && ($(this).data('module-rating') <= (rating_avg + 0.5))){
                    $(this).addClass('icon-star-half-full');
                }
                else{
                    $(this).addClass('icon-star-empty');
                }
                self.status[idx]= $(this).attr('class');
            });
            
        },

}
});
