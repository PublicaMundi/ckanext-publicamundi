
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
            window.console.warn('The jQuery extension "bootstrap-datepicker" is not loaded')
        }
        window.console.debug('Initialized module: datepicker')
    },
    teardown: function() { 
        window.console.debug('Tearing down module: datepicker')
    },
  }
})
