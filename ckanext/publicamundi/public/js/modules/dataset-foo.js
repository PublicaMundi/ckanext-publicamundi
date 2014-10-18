
this.ckan.module('input-contacts-foo', function ($, _) {
        
    return {
        options: {
            qname: null,
            terms: null,
        },

        initialize: function () 
        {
            var module = this, opts = this.options, qname = opts.qname, $el = this.el
            var $list = $el.children('ul')
            
            for (var key in opts.terms) {
                var yopts = { 
                    qname: qname + '.' + key, 
                    title: opts.terms[key].title
                }
                var $y = $list.children('li')
                    .filter(function () { return $(this).data('key') == key })
                if ($y.length) {
                    // The item allready exists
                    $.noop()
                } else {
                    // No item: create a <li> container, use the templated editor
                    $y = $('<li/>').data('key', key).appendTo($list)
                    $.extend(yopts, { template: 'default' })
                }
                $y.itemEditor(yopts)
            }
            
            window.console.log('Initialized module: input-contacts-foo')
        },

        teardown: function () { 
            window.console.log('Tearing down module: input-contacts-foo')
        },
    }
})

