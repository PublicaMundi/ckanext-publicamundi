(function () {

    var debug = $.proxy(window.console, 'debug')
    var warn = $.proxy(window.console, 'warn')
    
    var render = Mustache.render
    
    var ignore_event = function (ev) {
        var $curr_target = $(this)
        debug(' Ignored event at %s#%s: type=%s target=', 
            $curr_target.prop('tagName'), 
            $curr_target.attr('id') || 'undefined', 
            ev.type, 
            ev.target)
        return false
    }

    var warn_unexpected_event = function (ev) {
        warn('The %s event should be been handled at lower level', ev.type) 
    }
    
    var remove_self = function (ev) { 
        $(this).remove() 
    }

    var data_filter = function (key, val) {
        if (val) {
            return function () { 
                return $(this).data(key) == val
            }
        } else {
            return function () { 
                return $(this).data(key) != undefined
            } 
        }
    }

    this.ckan.module('edit-all-dict-items', function ($, _) {
        
        return {
            options: {
                title: null,
                qname: null,
                terms: null,
                messages: {},
            },

            initialize: function () 
            {
                var module = this,
                    $el = this.el,
                    opts = this.options, 
                    qname = opts.qname 
                    
                var $list = $el.children('ul')
                    .addClass('edit-all-dict-items')
                    .on('publicamundi-item_editor:remove', ignore_event)
                    .on('publicamundi-item_editor:create', ignore_event)
                    .on('publicamundi-item_editor:enable', ignore_event)
                    .on('publicamundi-item_editor:disable', ignore_event)
               
                for (var key in opts.terms) {
                    var $y, yopts
                    yopts = { 
                        qname: qname + '.' + key, 
                        title: opts.terms[key].title,
                        allowDelete: true,
                    }
                    $y = $list.children('li').filter(data_filter('key', key))
                    if (!$y.length) {
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
                this.el.children('ul').removeClass('edit-all-dict-items')
                debug('Tearing down module: edit-all-dict-items')
            },
        }
    })

    this.ckan.module('edit-selected-dict-items', function ($, _) {

        var editor_defaults = {
            index: null,
            allowDelete: true,
            onDelete: 'self-destroy',
        }
        
        return {
            options: {
                title: null,
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
                        '<i class="icon-asterisk"></i>{{label}}' + 
                    '</button>',
                pane: 
                    '<div class="add-item add-item-of-{{qname}}">' +
                        '{{{select}}} {{{addBtn}}}' + 
                    '</div>', 
            },
            
            _buildPanel: function ($list)
            {
                var templates = this.templates,
                    opts = this.options
                
                var $pane = $(render(templates.pane, { 
                    qname: opts.qname, 
                    select: '<select id="placeholder-1"></select>',
                    addBtn: '<button id="placeholder-2"></button>', 
                }))
                
                var $select = $(render(templates.select, { 
                    label: opts.messages['select-label'] || 'Specify a key' 
                }))
                
                var $add_btn = $(render(templates.addBtn, { 
                    label: opts.messages['add-label'] || 'Add' }))
                
                $pane.find('#placeholder-1').replaceWith($select)
                $pane.find('#placeholder-2').replaceWith($add_btn)
                
                $pane.insertBefore($list)
                
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

                return $pane
            },

            initialize: function () 
            {
                var module = this,
                    $el = this.el,
                    opts = this.options
                
                // Build a panel for select-n-add

                var $list = $el.children('ul'),
                    $pane = this._buildPanel($list),
                    $select = $pane.find('.select-key'),
                    $add_btn = $pane.find('.add-item')
                
                $list.addClass('edit-selected-dict-items')
                    .on('publicamundi-item_editor:remove', ignore_event)
                    .on('publicamundi-item_editor:create', ignore_event)
                    .on('publicamundi-item_editor:enable', ignore_event)
                    .on('publicamundi-item_editor:disable', ignore_event)
                
                // Initialize items

                var handle_destroy = function (ev) {
                    var $item = $(this).filter('li'),
                        key = $item.data('key')
                    if ($item.length) {
                        $('<option/>', { value: key })
                            .text(opts.terms[key].title)
                            .appendTo($select)
                        $item.remove()
                    }
                    return false
                }

                for (var key in opts.terms) {
                    var title = opts.terms[key].title
                    var $item = $list.children('li').filter(data_filter('key', key))
                    if ($item.length) {
                        $item.itemEditor($.extend({}, editor_defaults, { 
                            qname: opts.qname + '.' + key, 
                            title: title,
                        }))
                        $item.on('publicamundi-item_editor:destroy', handle_destroy)
                    } else {
                        $('<option/>', { value: key })
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
                            title = opts.terms[key].title
                        var $item = $('<li/>').data('key', key).appendTo($list)
                        $item.itemEditor($.extend({}, editor_defaults, { 
                            qname: opts.qname + '.' + key, 
                            title: title,
                            template: 'default',
                        }))
                        $item.on('publicamundi-item_editor:destroy', handle_destroy)
                        $select.find(':selected').remove()
                        $select.val('').trigger('change')
                        return false
                    })

                debug('Initialized module: edit-selected-dict-items', this.options)
            },
            teardown: function () 
            { 
                this.el.children('ul').removeClass('edit-selected-dict-items')
                debug('Tearing down module: edit-selected-dict-items', this.options)
            },
        };
    })

    this.ckan.module('edit-list-items', function ($, _) {

        var editor_defaults = {
            index: -1,
            allowDisable: false,
            onDelete: 'noop',
        }

        return {
            options: {
                title: null,
                qname: null,
                maxlength: 6,
                messages: {},
            },
            
            templates: {
                addBtn: 
                    '<button class="btn btn-small add-item" title="{{title}}">' + 
                        '<i class="icon-asterisk"></i>{{label}}' + 
                    '</button>',
                reorderBtn: 
                    '<button class="btn btn-small reorder-items" title="{{title}}">' + 
                        '<i class="icon-retweet"></i>{{label}}' + 
                    '</button>',
                clearBtn: 
                    '<button class="btn btn-small clear-items" title="{{title}}">' + 
                        '<i class="icon-eraser"></i>{{label}}' + 
                    '</button>',
                pane: 
                    '<div class="add-item add-item-of-{{qname}}">' +
                        '{{{addBtn}}} {{{reorderBtn}}} {{{clearBtn}}}' + 
                        '{{#description}}<span class="description">{{{description}}}</span>{{/description}}' + 
                    '</div>',
                clearAlert:
                    '<div>' + 
                        '<p class="message">{{message}}</p>' + 
                        '<div>' +
                            '<button class="btn btn-small btn-danger go-clear-items">{{clearLabel}}</button> ' +
                            '<button class="btn btn-small cancel-clear-items">{{cancelLabel}}</button>' +
                        '</div>' + 
                    '</div>'
            },

            _buildPanel: function ($list)
            {
                var templates = this.templates,
                    opts = this.options,
                    messages = opts.messages
                
                var $pane = $(render(templates.pane, { 
                    qname: opts.qname, 
                    addBtn: '<button id="placeholder-1"></button>',
                    reorderBtn: null, //'<button id="placeholder-2"></button>',
                    clearBtn: '<button id="placeholder-3"></button>',
                    description: messages['add-description'], 
                }))
                
                var $add_btn = $(render(templates.addBtn, { 
                    label: messages['add-label'] || 'Add',
                    title: messages['add-title']
                }))
                
                var $reorder_btn = $(render(templates.reorderBtn, { 
                    label: messages['reorder-label'] || 'Reorder', 
                    title: messages['reorder-title']
                }))
                
                var $clear_btn = $(render(templates.clearBtn, { 
                    label: messages['clear-label'] || 'Clear', 
                    title: messages['clear-title']
                }))
                
                $pane.find('#placeholder-1').replaceWith($add_btn)
                $pane.find('#placeholder-2').replaceWith($reorder_btn)
                $pane.find('#placeholder-3').replaceWith($clear_btn)
                
                $pane.insertBefore($list)
                
                return $pane
            },

            initialize: function () 
            {
                var module = this,
                    $el = this.el,
                    opts = this.options
                
                var $list = $el.children('ol'),
                    $pane = this._buildPanel($list),
                    $add_btn = $pane.find('.add-item'),
                    $reorder_btn = $pane.find('.reorder-items'),
                    $clear_btn = $pane.find('.clear-items')
                
                $list.addClass('edit-list-items')
                    .on('publicamundi-item_editor:create', ignore_event)
                    .on('publicamundi-item_editor:enable', ignore_event)
                    .on('publicamundi-item_editor:disable', ignore_event)
                    .on('publicamundi-item_editor:remove', warn_unexpected_event) 
                    .on('publicamundi-item_editor:destroy', warn_unexpected_event)

                // Initialize items 

                var num_items = 0

                var handle_remove = function (ev) {
                    var i = $(this).data('index'),
                        $items = $list.children('li')
                    assert(i == $items.index($(this)))
                    
                    // Shift items to the left 
                    
                    for (var j = i + 1; j < num_items; j++) {
                        $items.eq(j - 1)
                            .itemEditor('copyValues', $items.eq(j))
                    }
                    
                    // Destroy last item

                    $items.eq(num_items - 1)
                        .one('publicamundi-item_editor:destroy', function (ev1) {
                            $(this).remove()
                            num_items -= 1
                            return false
                        })
                        .hide({ 
                            duration: 400,
                            complete: function () {
                                $(this).itemEditor('destroy')
                            },
                        })
                    
                    return false
                }

                $list.children('li').each(function (i, li) {
                    var $item = $(li)
                    assert(i == $item.data('index'))
                    $item.itemEditor($.extend({}, editor_defaults, {
                        qname: opts.qname + '.' + i.toString(),
                        index: i,
                        canMoveUp: (i > 0),
                    }))
                    $item.on('publicamundi-item_editor:remove', handle_remove)
                    num_items += 1
                })

                // Bind event handlers
                
                $add_btn.on('click', function () {
                    var i = num_items
                    if (i == opts.maxlength) {
                        alert(render(opts.messages['maxlength-alert'], { 
                            maxlength: opts.maxlength }))
                    } else {
                        var $item = $('<li/>')
                            .data('index', i)
                            .itemEditor($.extend({}, editor_defaults, {
                                qname: opts.qname + '.' + i.toString(),
                                index: i,
                                canMoveUp: (i > 0),
                                template: 'default',
                             }))
                            .on('publicamundi-item_editor:remove', handle_remove)
                            .appendTo($list)
                        num_items += 1
                        setTimeout(function () {
                            $item.find(':input')
                                .not('.btn').not('[type=checkbox]').first()
                                .focus()
                        }, 500)
                    }
                    return false
                })
                
                $clear_btn.on('click', function () {
                    var messages = module.options.messages,
                        $btn = $(this)
                    $btn
                        .popover({ 
                            placement: 'right',
                            container: module.el,
                            html: true,
                            content: render(module.templates.clearAlert, {
                                message: render(messages['clear-alert'], { num: num_items }),
                                clearLabel: 'Clear',
                                cancelLabel: 'Cancel',
                            }) 
                        })
                        .popover('show')
                        .attr('disabled', 'disabled')
                    module.el.find('.btn.go-clear-items').one('click', function () {
                        module.el.children('ol').children('li').each(function (i, item) {
                            $(item)
                                .one('publicamundi-item_editor:destroy', function () {
                                    $(this).remove()
                                    num_items -= 1
                                    return false    
                                })
                                .itemEditor('destroy')
                        })
                        $btn
                            .popover('destroy')
                            .attr('disabled', null) 
                        return false
                    }) 
                    module.el.find('.btn.cancel-clear-items').one('click', function () {
                        $btn
                            .popover('destroy')
                            .attr('disabled', null) 
                        return false 
                    }) 
                    return false
                })

                $list.on('publicamundi-item_editor:move-up', function (ev) {
                    var $item = $(ev.target),
                        i = $item.data('index')
                    assert(i > 0)
                    var $prev_item = $(this).children('li').eq(i - 1)
                    $item.itemEditor('swapValues', $prev_item)
                    return false;
                })

                debug('Initialized module: edit-list-items opts=', this.options)
            },

            teardown: function () 
            { 
                this.el.children('ul').removeClass('edit-list-items')
                debug('Tearing down module: edit-list-items', this.options)
            },
        };
    })

    this.ckan.module('ababoua', function ($, _) {

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

}).apply(this)  
