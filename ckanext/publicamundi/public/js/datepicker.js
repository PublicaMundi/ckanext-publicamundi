
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

this.ckan.module('geodata-datepicker', function ($) {
  return {
    options: {
        // These options come from attribute keys so are always lowercase //
        dateformat: 'dd/mm/yy',
        altfield: null,
        altformat: null,
    },
    initialize: function () {
        var log = (window.console)? ($.proxy(window.console.log, window.console)) : ($.proxy(window.alert, window))
        var is_submitted = true
        var input = this.el
        var input_id = input.attr('id')
        var date = null

        if ($.datepicker) {
            /* Analyze the options from data-module-* attributes */
            var datepicker_opts = { 
                dateFormat: this.options.dateformat,
            }
            if (!(!this.options.altfield || !this.options.altformat)) {
                $.extend (datepicker_opts, {
                    altField:  this.options.altfield,
                    altFormat: this.options.altformat,
                })
                /* Must the original input must not be submitted with the form? */
                is_submitted = false
                date = new Date($(this.options.altfield).val())
            }
            /* Create the datepicker widget on this input */
            input.datepicker(datepicker_opts)
            log('A datepicker widget created on #'+(input_id)+" with "+JSON.stringify(datepicker_opts))
            /* Prevent this input from being submitted */
            if (!is_submitted) {
                input.closest('form').on('submit.datepicker', function () {
                    $('#'+input_id).attr('disabled', 'disabled')
                })
            }
            /* Assign an different initial value (if one exists) for the non-hidden input */
            if (date != null) {
                input.datepicker('setDate', date)
            }
        } else {
            log('No datepicker widget was found!')
        }
    },
  }
});

