
jQuery(document).ready(function ($) {
    
    var console = window.console
    var debug = $.proxy(console, 'debug') 
    // Autostart carousel
    $('#carousel-homepage').carousel();
});



