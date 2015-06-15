jQuery(document).ready(function ($) {
        var stars = null;
        var status = [];
        var rating_avg = null;

        initialize(); 
    
        function initialize() {
            
            var console = window.console;
            var debug = $.proxy(console, 'debug');

            stars = $('.package-rating a');
            stars.on('mouseenter', function(event){
                var hover = $(this);
                var hover_val = $(this).data('module-rating');
                stars.each(function(idx) {
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
                stars.each(function(idx) {
                    var prev = $(this).attr('class');
                    $(this).removeClass(prev);
                    $(this).addClass(status[idx]);
                })
            });

            update_status();
        };
        function update_status(){
                rating_avg = parseFloat($('#rating-average').text());
                stars.each(function(idx){
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
                    status.push($(this).attr('class'));
                });
                };

 
    });
