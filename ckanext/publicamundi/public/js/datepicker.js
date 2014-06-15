
this.ckan.module('datepicker', function ($, _) {
  return {
    options: {
        dateformat: 'yyyy-mm-dd',
    },
    initialize: function() {
        var module = this
        if ($.fn.datepicker) {
            $(this.el).datepicker({
                format: this.options.dateformat
            })
        }
        window.console.log('Initialized module: datepicker')
    },
    teardown: function() { 
        window.console.log('Tearing down module: datepicker')
    },
  }
})

