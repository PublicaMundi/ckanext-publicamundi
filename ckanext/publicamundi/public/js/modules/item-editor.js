
this.ckan.module('edit-all-dict-items', function ($, _) {
        
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
                $y.on('publicamundi-item_editor-destroyed', function (ev) {
                    $(this).remove()
                })
            }
            
            window.console.log('Initialized module: edit-all-dict-items')
        },

        teardown: function () { 
            window.console.log('Tearing down module: edit-all-dict-items')
        },
    }
})

