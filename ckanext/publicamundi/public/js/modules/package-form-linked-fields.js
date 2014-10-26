(function () {

    var debug = $.proxy(window.console, 'debug')
    var warn = $.proxy(window.console, 'warn')

    var render = Mustache.render
    
    this.ckan.module('package-form-linked-fields', function ($, _) {

        return {
            options: {
                target: null,
            },

            templates: {
                help: 
                    '<div class="help-block">This field is linked to {{{target}}}</div>',
                target:
                    '<em class="target-field">{{text}}</em>',
                targetLink:
                    '<a class="target-field btn-link">{{text}}</a>',
            },

            initialize: function () 
            {
                var module = this,
                    opts = this.options,
                    templates = this.templates
                
                var $target = $('form.dataset-form [name="'+opts.target.name+'"]')
                
                var $help = $(render(templates.help, { 
                    target: render(
                        ($target.length) ? (templates.targetLink) : (templates.target), 
                        { text: opts.target.title })
                }))
                
                module.el
                    .val(opts.target.value || $target.val())
                    .after($help)
                    .attr('disabled', 'disabled')
                
                if ($target.length) {
                    // Allow to navigate to the target input (or as closer to it)
                    $help.find('a.target-field')
                        .on('click', function () {
                            var $anchor = $target.is(':visible') ?
                                $target : $target.closest(':visible')
                            window.location.assign('#' + $anchor.attr('id'))
                            return false
                        })
                    // Keep in sync with target input
                    $target.on('change', function () {
                        module.el.val($(this).val())
                    })
                }

                debug('Initialized module: package-form-linked-fields with options:', opts)
            },

            teardown: function () 
            { 
                debug('Tearing down module: package-form-linked-fields')
            },
        };
    })

}).apply(this)  
