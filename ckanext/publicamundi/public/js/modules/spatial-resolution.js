(function () {

    var debug = $.proxy(window.console, 'debug')
    var warn = $.proxy(window.console, 'warn')
    
    this.ckan.module('input-spatial-resolution', function ($, _) {

        return {
            options: {
                qname: null,
            },

            initialize: function () 
            {
                var module = this,
                    $el = this.el,
                    opts = this.options 
                
                $el.find('input[type="radio"][name="' + opts.qname + '-type"]')
                    .on('change', function (ev) {
                        switch ($(ev.target).val()) {
                            case 'distance':
                                $el.find('input[name$=".distance"]').attr('disabled', null)
                                $el.find('input[name$=".uom"]').attr('disabled', null)
                                $el.find('input[name$=".denominator"]').attr('disabled', 'disabled')
                                break;
                            case 'scale':
                            default:
                                $el.find('input[name$=".distance"]').attr('disabled', 'disabled')
                                $el.find('input[name$=".uom"]').attr('disabled', 'disabled')
                                $el.find('input[name$=".denominator"]').attr('disabled', null)
                                break;
                        }
                    })
                

                debug('Initialized module: input-spatial-resolution opts=', opts)
            },

            teardown: function () 
            { 
                debug('Tearing down module: input-spatial-resolution')
            },
        };
    })

}).apply(this);
