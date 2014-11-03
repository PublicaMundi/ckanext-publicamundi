(function () {

    var debug = $.proxy(window.console, 'debug'),
        warn = $.proxy(window.console, 'warn'),
        assert = $.proxy(window.console, 'assert')

    var render = Mustache.render
    
    this.ckan.module('package-form-linked-fields', function ($, _) {

        return {
            options: {
                target: null, // Target descriptor
                submit: false, // Is this element to be submitted ?
                transform: null, // Transform target value before assignment 
                subscribeEvent: null, // Sync with target on certain sandbox events
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
                
                assert(module.el.is(':input')) 

                var $form = $('form.dataset-form')
                assert($form.length == 1)

                var target = '[name="' + opts.target.name + '"]',
                    $target = $form.find(target)
                 
                var $help = $(render(templates.help, { 
                    target: render(
                        ($target.length) ? (templates.targetLink) : (templates.target), 
                        { text: opts.target.title })
                }))
                
                var transform = opts.transform ?
                    (function (s) { return render(opts.transform, { target: s }) }) :
                    (function (s) { return s })

                module.el
                    .val(transform(opts.target.value || $target.val()))
                    .after($help)

                if (opts.submit) {
                    module.el.attr('readonly', 'readonly')
                } else {
                    module.el.attr('disabled', 'disabled')
                }

                if ($target.length) {
                    var sync = function () {
                        module.el.val(transform($target.val()))
                        return true
                    };
                    // Allow to navigate to the target input (or as closer to it)
                    $help.find('a.target-field')
                        .on('click', function () {
                            var $anchor = $target.is(':visible') ?
                                $target : $target.closest(':visible')
                            window.location.assign('#' + $anchor.attr('id'))
                            return false
                        })
                    // Try to keep in sync with target input
                    $target.on('change', sync)
                    if (opts.subscribeEvent) {
                        module.sandbox.subscribe(opts.subscribeEvent, sync)
                    }
                    // If to be submitted, always sync before submit
                    if (opts.submit) { 
                        $form.on('submit', sync)
                    }
                }

                debug('Initialized module: package-form-linked-fields with options:', opts)
            },

            teardown: function () 
            { 
                debug('Tearing down module: package-form-linked-fields')
            },
        };
    })

}).apply(this);

