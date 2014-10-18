
this.ckan.module('edit-all-dict-items', function ($, _) {
    
    var debug = $.proxy(window.console, 'debug')

    return {
        options: {
            qname: null,
            terms: null,
            messages: {},
        },

        initialize: function () 
        {
            var module = this,
                $el = this.el,
                opts = this.options, 
                qname = opts.qname, 
                $list = null 
                
            var remove_self = function () { 
                $(this).remove() 
            }
          
            var has_key = function (key) {
                return function () { 
                    return $(this).data('key') == key 
                }
            }

            $list = $el.children('ul')
            
            for (var key in opts.terms) {
                var $y, yopts
                yopts = { 
                    qname: qname + '.' + key, 
                    title: opts.terms[key].title,
                    allowDelete: true,
                }
                $y = $list.children('li').filter(has_key(key))
                if (!$y.length) {
                    // The item is missing: create <li> container, use the templated editor
                    $y = $('<li/>').data('key', key).appendTo($list)
                    $.extend(yopts, { template: 'default', disabled: true })
                }
                $y.itemEditor(yopts)
                $y.on('publicamundi-item_editor:destroy', remove_self)

            }
            
            debug('Initialized module: edit-all-dict-items')
        },

        teardown: function () 
        { 
            debug('Tearing down module: edit-all-dict-items')
        },
    }
})

this.ckan.module('edit-selected-dict-items', function ($, _) {
    
    var debug = $.proxy(window.console, 'debug')
    
    var render = Mustache.render

    return {
        options: {
            qname: null,
            terms: null,
            messages: {},
            select: 'select', // select|select2
        },

        templates: {
            select: 
                '<select class="select-key">' + 
                    '<option value="">{{label}}</option>' + 
                '<select/>',
            addBtn: 
                '<button class="btn btn-small add-item" title="{{title}}">' + 
                    '<i class="icon-asterisk"></i> {{label}}' + 
                '</button>',
            selectContainer: 
                '<div class="add-item add-item-of-{{qname}}">' +
                    '<select class="placeholder" /> <button class="placeholder" />' + 
                '</div>', 
        },

        initialize: function () 
        {
            var module = this,
                $el = this.el,
                opts = this.options,
                qname = opts.qname,
                templates = this.templates,
                handle_destroy = null
            
            var has_key = function (key) {
                return function () { 
                    return $(this).data('key') == key 
                }
            }
            
            // Build a container for select-n-add

            var $list, $select_container, $select, $add_btn

            $list = $el.children('ul')
            $select_container = $(render(templates.selectContainer, { qname: qname }))
            $select = $(render(templates.select, { 
                label: opts.messages['select-label'] || 'Specify a key' }))
            $add_btn = $(render(templates.addBtn, { 
                label: opts.messages['add-label'] || 'Add' }))
            $select_container.find('select.placeholder').replaceWith($select)
            $select_container.find('button.placeholder').replaceWith($add_btn)
            $select_container.insertBefore($list)
            
            switch (opts.select) {
                case 'select2':
                    $select.select2({
                        placeholder: 0,
                        width: 'element', 
                        minimumResultsForSearch: 12, 
                        allowClear: 1, 
                    })       
                    break;
                case 'select':
                default:
                    break;
            }
            
            // Initialize items

            handle_destroy = function (ev) {
                var $item = $(this).filter('li'),
                    key = $item.data('key')
                if ($item.length) {
                    $('<option/>')
                        .attr('value', key)
                        .text(opts.terms[key].title)
                        .appendTo($select)
                    $item.remove()
                }
                return false
            }

            for (var key in opts.terms) {
                var title = opts.terms[key].title
                var $item = $list.children('li').filter(has_key(key))
                if ($item.length) {
                    $item.itemEditor({ 
                        qname: qname + '.' + key, 
                        title: title, 
                        allowDelete: 1, })
                    $item.on('publicamundi-item_editor:destroy', handle_destroy)
                } else {
                    $('<option/>')
                        .attr('value', key)
                        .text(title)
                        .appendTo($select)
                }
            }
            
            // Bind event handlers

            $select
                .on('change', function (ev) {
                    var k = $(this).val()
                    $add_btn.attr('disabled', (k)? null:'disabled')
                })
            
            $add_btn
                .attr('disabled', 'disabled')
                .on('click', function (ev) {
                    var key = $select.val(), 
                        title = opts.terms[key].title,
                        $item = null
                    $item = $('<li/>').data('key', key).appendTo($list)
                    $item.itemEditor({ 
                        qname: qname + '.' + key, 
                        title: title,
                        template: 'default',
                        allowDelete: 1, })
                    $item.on('publicamundi-item_editor:destroy', handle_destroy)
                    $select.find(':selected').remove()
                    $select.trigger('change')
                    return false
                })

            debug('Initialized module: edit-selected-dict-items', this.options)
        },
        teardown: function () 
        { 
            debug('Tearing down module: edit-selected-dict-items', this.options)
        },
    };
})

this.ckan.module('ababoua', function ($, _) {
    
    var debug = $.proxy(window.console, 'debug')

    return {
        options: {
            boo: 'Boo',
        },

        initialize: function () 
        {
            var module = this,
                $el = this.el,
                opts = this.options 
            
            debug('Initialized module: ababoua opts=', opts)
        },
        teardown: function () 
        { 
            debug('Tearing down module: ababoua', this.options)
        },
    };
})
