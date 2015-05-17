
jQuery(document).ready(function ($) {
    
    var console = window.console
    var debug = $.proxy(console, 'debug') 
    console.log("hello"); 
    // Autostart carousel
    $('#carousel-homepage').carousel();
});



