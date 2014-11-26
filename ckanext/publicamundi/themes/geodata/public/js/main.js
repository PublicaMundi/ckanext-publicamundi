function myFunction() {
        var obj = $('.nav-pills > li > a[href$="/group"]');
        
        // Mouse enter and leave listeners on groups button
        obj.on('mouseenter', function(){
            $('#menu-block').addClass('enabled');
            $('#menu-block-home').addClass('enabled');
            obj.parent().addClass('painted');
        });
        obj.on('mouseleave', function(){
            $('#menu-block').removeClass('enabled');
            $('#menu-block-home').removeClass('enabled');
            obj.parent().removeClass('painted');
        });

        // Add listeners also on menu itself to keep it enabled
        $('#menu-block').on('mouseenter', function(){
            $('#menu-block').addClass('enabled');
            obj.parent().addClass('painted');
        });
        $('#menu-block').on('mouseleave', function(){
            $('#menu-block').removeClass('enabled');
            obj.parent().removeClass('painted');
        });
        $('#menu-block-home').on('mouseenter', function(){
            $('#menu-block-home').addClass('enabled');
            obj.parent().addClass('painted');
        });
        $('#menu-block-home').on('mouseleave', function(){
            $('#menu-block-home').removeClass('enabled');
            obj.parent().removeClass('painted');

        });

        //Upload button hover
        $('.image-upload input[type="file"]').on('mouseenter', function(){
            $(this).parent().find('.btn:first').addClass('btn-hover');
            //$(this).parent().find('.btn:first').addClass('btn-hover');
        });

        $('.image-upload input[type="file"]').on('mouseleave', function(){
            
            $(this).parent().find('.btn:first').removeClass('btn-hover');
            //$(this).parent().find('.btn:first').removeClass('btn-hover');
        });

        //Breadcrumbs auto hide all but last element
    
           brd_items = $('.breadcrumb li:first').next().nextAll();
           brd_items = brd_items.not(':last');

            brd_items.each(function(idx) {
                //console.log($(this).context.innerText);
                //$(this).context.innerText = "...";
                $(this).addClass('breadcrumb-hide-text');
            });
            brd_items.on('mouseenter', function(){
                $(this).removeClass('breadcrumb-hide-text');
            });
            brd_items.on('mouseleave', function(){
                $(this).addClass('breadcrumb-hide-text');
            });

}
onload = myFunction;
