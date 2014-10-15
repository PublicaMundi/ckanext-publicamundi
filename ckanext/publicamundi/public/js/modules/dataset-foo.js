
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


//
// Without helper ckanext.publicamundi.* widgets
//

this.ckan.module('input-contacts-foo-1', function ($, _) {
        
    return {
        options: {
            qname: null,
            terms: null,
            titles: null,
        },
        initialize: function () 
        {
            var module = this, qname = this.options.qname, $el = this.el
            
            var $list = $el.children('ul')
            var $existing_items = $list.children('li')   
            var existing_keys = $existing_items
                .map(function (i, y) { return $(y).data('key') })
                .get()

            module.keys = {}
            for (k in module.options.terms) {
                if ($.inArray(k, existing_keys) >= 0) {
                    module.keys[k] = true
                    module._prepareEditorWidget(k)
                } else {
                    var $placeholder = module._createPlaceholderWidget(k)
                    $('<li>').data('key', k)
                        .append($placeholder)
                        .appendTo($list)
                    module.keys[k] = false
                }
            }
           
            var $item_tpl = $el.find(
                'script#' + qname.replace(/[.]/g, '\\.') + '-item-template')
            module.templates['editor-widget'] = $item_tpl.text()

            window.console.log('Initialized module: input-contacts-foo')
        },
        teardown: function () { 
            window.console.log('Tearing down module: input-contacts-foo')
        },
        templates: {
            'remove-btn': 
                '<a class="btn btn-small pull-right remove-object" title="{{title}}"><i class="icon-remove"></i> {{label}}</a>',
            'edit-btn':
                '<a class="btn btn-small pull-right edit-object" title="{{title}}"><i class="icon-pencil"></i> {{label}}</a>',
            'placeholder-widget':
                '<div><header><h3 class="inline">{{title}}</h3><span class="label not-available">n/a</span> {{{edit-btn}}}</header></div>',
        },
        
        // Helpers
        
        _renderTemplate: function (name, data)
        {
            return Mustache.render(this.templates[name], data)
        },
        _createPlaceholderWidget: function (key)
        {
            var module = this, qname = this.options.qname, $el = this.el
            
            var $placeholder_widget = $(module._renderTemplate('placeholder-widget', {
                'title': module.options.terms[key].title,
                'edit-btn': module._renderTemplate('edit-btn', { 
                    label: 'Create', title: 'Provide info for this contact',
                }),
            }))

            var $edit_btn = $placeholder_widget.find('header > .btn')
            $edit_btn
                .on('click', function () { 
                    var $editor_widget = module._createEditorWidget(key)
                    $(this).closest('li').empty().append($editor_widget)
                    module._prepareEditorWidget(key)
                    module.keys[key] = true
                    window.console.info('Added an item widget keyed at "'+key+'"')
                })
                .on('mouseover', function () { 
                    $placeholder_widget.css({'background-color': '#f7f7f7',})
                }) 
                .on('mouseout', function () { 
                    $placeholder_widget.css({'background-color':'inherit',}) 
                }) 

            return $placeholder_widget
        },
        _createEditorWidget: function (key)
        {
            // Create an editor widget based on the provided (Mustache) template
            
            var module = this, qname = this.options.qname, $el = this.el
            
            var $editor_widget = module._renderTemplate('editor-widget', {
                'key': key,
                'title': module.options.terms[key].title,
            })
           
            return $editor_widget
        },
        _prepareEditorWidget: function (key)
        {
            var module = this, qname = this.options.qname, $el = this.el

            var $y = $el.children('ul').children('li')
                .filter(function () { return $(this).data('key') == key })
            var widget_selector = 'div.widget'
                + '.object-qname-' + (qname + '.' + key).replace(/[.]/g, '\\.')
            
            var $widget = $y.find(widget_selector)
            var $widget_header = $widget.children('header')
            var $remove_btn = $(module._renderTemplate('remove-btn', { label: 'Remove' }))
            $remove_btn
                .on('click', function () { 
                    $y.fadeOut(400, 'swing', function () { 
                        var $placeholder = module._createPlaceholderWidget(key)
                        $(this).empty().append($placeholder).fadeIn()
                        module.keys[key] = false
                        window.console.info('Removed item widget keyed at "'+key+'"')
                    })
                })
                .on('mouseover', function () { 
                    $widget.css({'background-color': '#f7f7f7',})
                }) 
                .on('mouseout', function () { 
                    $widget.css({'background-color':'inherit',}) 
                }) 
            $widget_header.children('h3').addClass('inline')
            $widget_header.append($remove_btn)
        },
    }
})

