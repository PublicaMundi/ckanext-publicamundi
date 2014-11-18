function myFunction() {
        var obj = $('.nav-pills > li > a[href="/group"]');
        
        // Mouse enter and leave listeners on groups button
        obj.on('mouseenter', function(){
            $('#menu-block').addClass('enabled');
            $('#menu-block-home').addClass('enabled');
        });
        obj.on('mouseleave', function(){
            $('#menu-block').removeClass('enabled');
            $('#menu-block-home').removeClass('enabled');
        });

        // Add listeners also on menu itself to keep it enabled
        $('#menu-block').on('mouseenter', function(){
            $('#menu-block').addClass('enabled');
        });
        $('#menu-block').on('mouseleave', function(){
            $('#menu-block').removeClass('enabled');
        });
        $('#menu-block-home').on('mouseenter', function(){
            $('#menu-block-home').addClass('enabled');
        });
        $('#menu-block-home').on('mouseleave', function(){
            $('#menu-block-home').removeClass('enabled');

        });

}
onload = myFunction;
