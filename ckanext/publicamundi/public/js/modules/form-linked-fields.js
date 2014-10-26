(function () {

    var debug = $.proxy(window.console, 'debug')
    var warn = $.proxy(window.console, 'warn')

    var render = Mustache.render
    
    this.ckan.module('form-linked-fields', function ($, _) {

        return {
            options: {
                target: null,
                name: null,
            },

            templates: {
                help:
                    '<div class="help-block">' + 
                        'This field is linked to <a class="target-field btn-link">{{name}}</a></div>',
            },

            initialize: function () 
            {
                var module = this,
                    opts = this.options
                
                var $target = $('.dataset-form [name="'+opts.target+'"]')
                
                var $help = $(render(module.templates.help, { name: opts.name }))
                
                module.el
                    .val($target.val())
                    .after($help)
                    .prop('disabled', 'disabled')
                
                $help.find('a.target-field')
                    .on('click', function () {
                        var $a = $target.is(':visible') ?
                            $target : $target.closest(':visible')
                        window.location.assign('#' + $a.attr('id'))
                        return false
                    })

                $target.on('change', function () {
                    module.el.val($(this).val())
                })

                debug('Initialized module: form-linked-fields with options:', opts)
            },

            teardown: function () 
            { 
                debug('Tearing down module: form-linked-fields')
            },
        };
    })

}).apply(this)  
