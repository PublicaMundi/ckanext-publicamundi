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
                    '<div class="help-block">This field is linked to <a href="#{{id}}">{{name}}</a></div>',
            },

            initialize: function () 
            {
                var module = this,
                    opts = this.options,
                    $target = null
                
                $target = $('.dataset-form [name="'+opts.target+'"]')
                
                module.el
                    .val($target.val())
                    .prop('disabled', 'disabled')

                module.el.after(
                    $(render(module.templates.help, { 
                        name: opts.name, id: $target.attr('id') })))

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
