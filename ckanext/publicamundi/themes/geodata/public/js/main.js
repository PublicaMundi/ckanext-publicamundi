function myFunction() {
        var obj = $('.nav-pills > li > a[href="/group"]');
        
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

        //Upload button hover bypass
        $('.controls input').on('mouseenter', function(){
            $(this).parent().find('.btn:first').addClass('btn-hover');
        });

        $('.controls input').on('mouseleave', function(){
            $(this).parent().find('.btn:first').removeClass('btn-hover');
        });


}
onload = myFunction;
