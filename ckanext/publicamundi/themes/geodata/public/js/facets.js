jQuery(document).ready(function ($, _) {
    
    var console = window.console
    var debug = $.proxy(console, 'debug') 
    
    handleFacets();
});

var LIMIT = 5;

function handleFacets() {
    
    // Initially hide facet items with index over LIMIT
    function init_hide(){
        var cat_list = $('.secondary .nav-facet');
        cat_list.each(function(index){
            $(this).addClass('li-hidden');
            
            var list = $(this).find('li');
            list.each(function(index){
                if (index>LIMIT){
                    $(this).css("display","none");
                }
                if (index==LIMIT){
                        $(this).addClass("no-bottom-border");
                }

            });

        });
    };
    init_hide();
    
    // Facet Show more/less handling
    function show_more(e){
        e.preventDefault();
        var ul = $(this).parent().parent().find('.nav-facet');
        var list = ul.find('li');
        var title = ul.attr('title');
    
        //$(this).parent().parent().find('.read-more').text("Show Only Popular ");
        //list.parent().addClass("li-hidden");
        $(this).parent().parent().find('.read-more').addClass("hidden");
        $(this).parent().parent().find('.read-less').removeClass("hidden");

        list.parent().removeClass('li-hidden');
        list.each(function(index){
            $(this).css("display","block");
            $(this).removeClass("no-bottom-border");
        });
        $('.read-less').one('click', show_less);
    };
        function show_less(e){
        e.preventDefault();            
        var ul = $(this).parent().parent().find('.nav-facet');
        var list = ul.find('li');
        var title = ul.attr('title');

        //$(this).parent().parent().find('.read-more').text("Show More");
        $(this).parent().parent().find('.read-less').addClass("hidden");
        $(this).parent().parent().find('.read-more').removeClass("hidden");

        if (list.length >= LIMIT){
            list.parent().addClass("li-hidden");
        }
        list.each(function(index){
            if (index > LIMIT){
                $(this).css("display", "none");
            };
            if (index == LIMIT){
                $(this).addClass("no-bottom-border");
            }
        });
        $('.read-more').one('click', show_more);
    };

    $('.read-less').one('click', show_less);
    $('.read-more').one('click', show_more);

    // Sort by popularity ascending/descending handling
    function sort_count_up(e) {
        //ascending count sort
        function asc_count_sort(a, b) {
            return parseInt($(b).attr("count")) < parseInt($(a).attr("count")) ? 1 : -1;
        };
        e.preventDefault();
        //$(this).text("1 -> 9");
        //$(this).parent().find('.sort-name').text("A    Z");
        $(this).addClass("up");
        $(this).removeClass("down");
        $(this).parent().find('.sort-name').removeClass("down");
        $(this).parent().find('.sort-name').removeClass("up");
        var ul = $(this).parent().parent().parent().find('.nav-facet');
        var list = ul.find('li');

        ul.toggleClass("count_asc");
        ul.toggleClass("count_desc");
        list.sort(asc_count_sort).appendTo(ul);
        if (ul.hasClass("li-hidden")){
            list.each(function(index){
                $(this).removeClass("no-bottom-border");
                if (index<=LIMIT){
                    $(this).css("display","block");
                    if (index==LIMIT){
                        $(this).addClass("no-bottom-border");
                    }
                }
                else{
                    $(this).css("display","none");
                }
            });
        }
        
        $(this).one('click', sort_count_down);
    };
    
    function sort_count_down(e) {
        //descending count sort
        function desc_count_sort(a, b) {
            return parseInt($(b).attr("count")) > parseInt($(a).attr("count")) ? 1 : -1;
        };

        //$(this).text("1 <- 9");
        //$(this).parent().find('.sort-name').text("A    Z");
        $(this).addClass("down");
        $(this).removeClass("up");
        $(this).parent().find('.sort-name').removeClass("down");
        $(this).parent().find('.sort-name').removeClass("up");
        e.preventDefault();
        var ul = $(this).parent().parent().parent().find('.nav-facet');
        var list = ul.find('li');

        ul.toggleClass("count_asc");
        ul.toggleClass("count_desc");
        list.sort(desc_count_sort).appendTo(ul);
        
        if (ul.hasClass("li-hidden")){
            list.each(function(index){
                $(this).removeClass("no-bottom-border");
                if (index<= LIMIT){
                    $(this).css("display","block");
                    if (index==LIMIT){
                        $(this).addClass("no-bottom-border");
                    }

                }
                else{
                    $(this).css("display","none");
                }
            });
        }

        $(this).one('click', sort_count_up);
    };
    
    
            
    // Sort alphabetically ascending/descending handling
    function sort_name_up(e) {
        function remove_accented(str) {
            return str.replace('Ά', 'Α').replace('Έ', 'Ε').replace('Ή', 'Η').replace('Ί', 'Ι').replace('Ό', 'Ο').replace('Ύ', 'Υ').replace('Ώ', 'Ω');
        }

        //ascending alphabetical sort
        function asc_alpha_sort(a, b) {
            return (remove_accented($(b).text().toUpperCase())) < (remove_accented($(a).text().toUpperCase()))? 1 : -1;
        };

        //$(this).text("A -> Z");
        //$(this).parent().find('.sort-count').text("1    9");
        $(this).addClass("down");
        $(this).removeClass("up");
        $(this).parent().find('.sort-count').removeClass("down");
        $(this).parent().find('.sort-count').removeClass("up");
        e.preventDefault();
        var ul = $(this).parent().parent().parent().find('.nav-facet');
        var list = ul.find('li');
        ul.toggleClass("name_asc");
        ul.toggleClass("name_desc");
        list.sort(asc_alpha_sort).appendTo(ul);
        
        if (ul.hasClass("li-hidden")){
            list.each(function(index){
                $(this).removeClass("no-bottom-border");
                if (index<=LIMIT){
                    $(this).css("display","block");
                    if (index==LIMIT){
                        $(this).addClass("no-bottom-border");
                    }

                }
                else{
                    $(this).css("display","none");
                }
            });
        }

        $(this).one('click', sort_name_down);
    };
    function sort_name_down(e) {
        //remove greek accented characters
        function remove_accented(str) {
            return str.replace('Ά', 'Α').replace('Έ', 'Ε').replace('Ή', 'Η').replace('Ί', 'Ι').replace('Ό', 'Ο').replace('Ύ', 'Υ').replace('Ώ', 'Ω');
        }
        //descending alphabetical sort
        function desc_alpha_sort(a, b) {
            return (remove_accented($(b).text().toUpperCase())) > (remove_accented($(a).text().toUpperCase()))? 1 : -1;
        };

        //$(this).text("A <- Z");
        //$(this).parent().find('.sort-count').text("1    9");
        $(this).addClass("up");
        $(this).removeClass("down");
        $(this).parent().find('.sort-count').removeClass("down");
        $(this).parent().find('.sort-count').removeClass("up");
        e.preventDefault();
        var ul = $(this).parent().parent().parent().find('.nav-facet');
        var list = ul.find('li');

        ul.toggleClass("name_asc");
        ul.toggleClass("name_desc");
        list.sort(desc_alpha_sort).appendTo(ul);
        
        if (ul.hasClass("li-hidden")){
            list.each(function(index){
                $(this).removeClass("no-bottom-border");
                if (index<=LIMIT){
                    $(this).css("display","block");
                    if (index==LIMIT){
                        $(this).addClass("no-bottom-border");
                    }

                }
                else{
                    $(this).css("display","none");
                }
            });
        }

        $(this).one('click', sort_name_up);
    };

    $('.sort-count').one('click', sort_count_up);
    $('.sort-name').one('click', sort_name_up);

}
