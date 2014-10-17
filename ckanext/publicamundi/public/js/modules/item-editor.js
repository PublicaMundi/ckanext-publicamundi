
this.ckan.module('edit-all-dict-items', function ($, _) {
    
    var debug = $.proxy(window.console, 'debug')

    return {
        options: {
            qname: null,
            terms: null,
        },

        initialize: function () 
        {
            var module = this,
                $el = this.el,
                opts = this.options, 
                qname = opts.qname, 
                $list = $el.children('ul'),
                remove_self = function () { $(this).remove() }
            
            for (var key in opts.terms) {
                var yopts = { 
                    qname: qname + '.' + key, 
                    title: opts.terms[key].title,
                    allowDelete: true,
                }
                var $y = $list.children('li')
                    .filter(function () { return $(this).data('key') == key })
                if ($y.length) {
                    // The item allready exists
                    $.noop()
                } else {
                    // No item: create a <li> container, use the templated editor
                    $y = $('<li/>').data('key', key).appendTo($list)
                    $.extend(yopts, { template: 'default', disabled: true })
                }
                $y.itemEditor(yopts)
                $y.on('publicamundi-item_editor:destroy', remove_self)
            }
            
            debug('Initialized module: edit-all-dict-items')
        },

        teardown: function () { 
            debug('Tearing down module: edit-all-dict-items')
        },
    }
})


this.ckan.module('ababoua', function ($, _) {
    var debug = $.proxy(window.console, 'debug')

    return {
        options: {
            boo: 'Boo',
        },

        initialize: function () 
        {
            debug('Initialized module: ababoua', this.options)
        },
        teardown: function () { 
            debug('Tearing down module: ababoua', this.options)
        },
    };
})
