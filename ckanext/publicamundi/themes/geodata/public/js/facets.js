jQuery(document).ready(function ($) {
    
    var console = window.console
    var debug = $.proxy(console, 'debug') 
    
    handleFacets();
});

var LIMIT = 4;

function handleFacets() {
    
    // Initially hide facet items with index over LIMIT
    function init_hide(){
        var cat_list = $('.secondary .nav-facet');
        console.log(cat_list);
        cat_list.each(function(index){
            $(this).addClass('li-hidden');
            
            var list = $(this).find('li');
            console.log(list);
            list.each(function(index){
                if (index>LIMIT){
                    $(this).css("display","none");
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
    
        $(this).parent().parent().find('.read-more').text("Show Only Popular " + title);

        list.parent().removeClass('li-hidden');
        list.each(function(index){
            $(this).css("display","block");
        });
        $(this).one('click', show_less);
    };
        function show_less(e){
        e.preventDefault();            
        var ul = $(this).parent().parent().find('.nav-facet');
        var list = ul.find('li');
        var title = ul.attr('title');

        $(this).parent().parent().find('.read-more').text("Show More "+title);
        if (list.length >= LIMIT){
            list.parent().addClass("li-hidden");
        }
        list.each(function(index){
            if (index > LIMIT){
                $(this).css("display", "none");
            };
        });
        $(this).one('click', show_more);
    };

    $('.read-more').one('click', show_more);

    // Sort by popularity ascending/descending handling
    function sort_count_up(e) {
        //ascending count sort
        function asc_count_sort(a, b) {
            return parseInt($(b).attr("count")) < parseInt($(a).attr("count")) ? 1 : -1;
        };
        e.preventDefault();
        $(this).text("1>9");
        $(this).parent().find('.sort-name').text("A-Z");
        var ul = $(this).parent().parent().find('.nav-facet');
        var list = ul.find('li');

        ul.toggleClass("count_asc");
        ul.toggleClass("count_desc");
        list.sort(asc_count_sort).appendTo(ul);
        if (ul.hasClass("li-hidden")){
            list.each(function(index){
                if (index<=LIMIT){
                    $(this).css("display","block");
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

        $(this).text("1<9");
        $(this).parent().find('.sort-name').text("A-Z");
        e.preventDefault();
        var ul = $(this).parent().parent().find('.nav-facet');
        var list = ul.find('li');

        ul.toggleClass("count_asc");
        ul.toggleClass("count_desc");
        list.sort(desc_count_sort).appendTo(ul);
        
        if (ul.hasClass("li-hidden")){
            list.each(function(index){
                if (index<= LIMIT){
                    $(this).css("display","block");
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
        //ascending alphabetical sort
        function asc_alpha_sort(a, b) {
            return ($(b).text().toUpperCase()) < ($(a).text().toUpperCase())? 1 : -1;
        };

        $(this).text("A>Z");
        $(this).parent().find('.sort-count').text("1-9");
        e.preventDefault();
        var ul = $(this).parent().parent().find('.nav-facet');
        var list = ul.find('li');

        ul.toggleClass("name_asc");
        ul.toggleClass("name_desc");
        list.sort(asc_alpha_sort).appendTo(ul);
        
        if (ul.hasClass("li-hidden")){
            list.each(function(index){
                if (index<=LIMIT){
                    $(this).css("display","block");
                }
                else{
                    $(this).css("display","none");
                }
            });
        }

        $(this).one('click', sort_name_down);
    };
    function sort_name_down(e) {
        //descending alphabetical sort
        function desc_alpha_sort(a, b) {
            return ($(b).text().toUpperCase()) > ($(a).text().toUpperCase())? 1 : -1;
        };

        $(this).text("A<Z");
        $(this).parent().find('.sort-count').text("1-9");
        e.preventDefault();
        var ul = $(this).parent().parent().find('.nav-facet');
        var list = ul.find('li');

        ul.toggleClass("name_asc");
        ul.toggleClass("name_desc");
        list.sort(desc_alpha_sort).appendTo(ul);
        
        if (ul.hasClass("li-hidden")){
            list.each(function(index){
                if (index<=LIMIT){
                    $(this).css("display","block");
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
