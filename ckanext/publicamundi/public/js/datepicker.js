
this.ckan.module('datepicker', function ($, _) {
  return {
    options: {
        format: 'yyyy-mm-dd',
    },
    initialize: function() {
        var module = this
        if ($.fn.datepicker) {
            $(this.el).datepicker({
                format: module.options.format
            })
        } else {
            window.console.error('The jQuery extension "bootstrap-datepicker" is not loaded')
        }
        window.console.log('Initialized module: datepicker')
    },
    teardown: function() { 
        window.console.log('Tearing down module: datepicker')
    },
  }
})

