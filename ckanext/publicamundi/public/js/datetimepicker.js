
this.ckan.module('datetimepicker', function ($, _) {
  return {
    options: {
        picktime: true,
        pickdate: true,
        pickseconds: true,
        pick12hourformat: false,
        format: 'yyyy-MM-dd hh:mm',
    },
    initialize: function() {
        var module = this
        if ($.fn.datetimepicker) {
            var $el = $(this.el) 
            var $input = $el.find('input')
            $input.data('format', module.options.format)
            $el.datetimepicker({
                pickTime: module.options.picktime,
                pickDate: module.options.pickdate,
                pickSeconds: module.options.pickseconds,
                pick12HourFormat: module.options.pick12hourformat,
            })
        } else {
            window.console.error('The jQuery extension "bootstrap-datetimepicker" is not loaded')
        }
        window.console.log('Initialized module: datetimepicker')
    },
    teardown: function() { 
        window.console.log('Tearing down module: datetimepicker')
    },
  }
})

