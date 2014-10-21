
jQuery(document).ready(function ($) {
    
    var console = window.console
        debug = $.proxy(console, 'debug') 
        warn = $.proxy(console, 'warn')
        error = $.proxy(console, 'error')
        assert = $.proxy(console, 'assert')

    var render = Mustache.render 
    
    // Enumerate events triggered by following widgets
    var widget_events = {
        // fieldwidget
        Create: 'create',   // when was (fully) created
        Destroy: 'destroy', // when was destroyed
        Enable: 'enable',   // when was enabled
        Disable: 'disable', // when was disabled
        // itemEditor
        Remove: 'remove',   // when is requested to be removed (but not destroyed yet) 
        MoveUp: 'move-up',  // when is requested to move upwards 
    }
    
    // Parse a dot-delimited qialified name
    var parse_name = function (qname) {
        var i = qname.lastIndexOf('.')
        return {
            qname: qname,
            namePrefix: (i > 0)? qname.substring(0, i) : null,
            nameKey: (i > 0)? qname.substring(i + 1) : qname,
        }
    }
    
    // A name filter for elements
    var name_filter = function (name) {
        return function () {
            return $(this).attr('name') == name
        }
    }

    // Define widgets

    $.widget('publicamundi.fieldwidget', {
        options: {
            qname: null,
            title: null,
            template: null,
            defaultTemplate: function (name) {
                return 'script#' + name.qname.replace(/[.]/g, '\\.') + '-template' 
            },
            classPrefix: 'field-qname-',
            hide: { duration: 600, delay: 0 },
            show: { duration: 600, delay: 0, easing: 'swing' },
        },

        _create: function()
        {
            var opts = this.options, tpl = null, dat = null
            
            this.name = parse_name(opts.qname)
            this.title = opts.title
            
            // Preprocess template-related options

            if (opts.template) {
                // The field widget doesnt exist, it must be created from a template
                if ($.isPlainObject(opts.template)) {
                    tpl = opts.template.source || 'default'
                    dat = opts.template.data
                    dat = $.isEmptyObject(dat)? {} : Object.create(dat)
                } else {
                    tpl = opts.template.toString()
                    dat = {}
                }
                if (tpl instanceof jQuery) {
                    tpl = tpl.text()
                } else {
                    tpl = $.trim(tpl.toString())
                    if (tpl.lastIndexOf('<', 0) != 0) {
                        // assume it's a selector
                        if (tpl == 'default')
                            tpl = opts.defaultTemplate(this.name)  
                        tpl = $(tpl).text()
                    }
                }
            }     
            
            // Create in the requested (enabled/disabled) mode, fire proper events

            if (opts.disabled) {
                this._createDisabled(tpl, dat)
                this._trigger(widget_events.Disable)
            } else {
                this._createEnabled(tpl, dat)
                this._trigger(widget_events.Enable)
            }
            
            // Setup (delegated) event handlers
            
            this._setupEvents()

            // Done

            if (!this.title) { 
                this.title = this._extractTitle() 
            }
            
            this._refresh()
        },
        
        _refresh: function()
        {
            $.noop()
        },

        destroy: function()
        {
            // Cleanup events and attributes.
            // Note: It will delegate to this._destroy() for widget-specific cleanup
            this._super()
            // When finished, fire the proper event
            this._trigger(widget_events.Destroy)
        },

        _destroy: function()
        {
            var opts = this.options
            
            if (opts.template) {
                this.element.empty()
            }
        },
        
        _setOptions: function() 
        { 
            this._superApply(arguments);
            this._refresh();
        },

        _setOption: function (key, value)
        {
            switch (key) {
                case 'disabled':
                    warn('You can enable/disable the "' + this.widgetFullName + 
                        '" widget using the namesake methods')
                    break;
                case 'qname':
                case 'template':
                case 'classPrefix':
                    warn('The option (' + key + ') ' +
                        'cannot be changed after widget\'s creation')
                    break;
                default:
                    this._super(key, value);
                    break;
            }
        },

        enable: function()
        {
            var p = true

            if (this.options.disabled === true) {
                this.options.disabled = undefined // in progress
                p = this._enable()
                p.done(function () {
                    this.options.disabled = false
                    this._trigger(widget_events.Enable)
                })
            }

            return p
        },
       
        disable: function()
        {
            var p = true
            
            if (this.options.disabled === false) {
                this.options.disabled = undefined // in progress
                p = this._disable()
                p.done(function () {
                    this.options.disabled = true
                    this._trigger(widget_events.Disable)
                })
            }

            return p
        },

        // Base implementation

        _buildControlFromTemplate: function (tpl, data)
        {
            var $control = null,
                widget = this,
                event_prefix = this.widgetEventPrefix
            
            // Generate from template

            this._debug('About to generate control')
            
            $.extend(data, this._getTemplateVars())
            $control = $(render(tpl, data))
            
            assert($control.hasClass('field-widget'))
            assert($control.hasClass(this.options.classPrefix + this.name.qname))

            // Instantiate ckan module instances (when enabled)

            this.element.one(event_prefix + widget_events.Enable, function () {
                widget._debug('About to instantiate ckan modules')
                $control.find('[data-module]').each(function (i, el) {
                    ckan.module.initializeElement(el)
                })
            })

            return $control
        },

        _queryControl: function ()
        {
            var qname = this.name.qname, opts = this.options, $control = null
            var selector = '.field-widget'
                + ('.' + opts.classPrefix + qname.replace(/[.]/g, '\\.'))
            
            $control = this.element.children(selector)
            assert($control.length == 1)

            return $control
        },

        _createEnabled: function (tpl, data)
        {
            if (tpl) {
                // Generate from template
                this.$control = this._buildControlFromTemplate(tpl, data)
                this.element.empty().append(this.$control)
            } else {
                // The field-widget already exists, use it
                this.$control = this._queryControl()
            }
        },
        
        _createDisabled: function (tpl, data)
        {
            // In this base implementation, we just create our widget in enabled mode,
            // and then we immediately disable it. But, a derived widget may choose to
            // do different things (such as to lazily load actual this.$control when this
            // is really needed).
            
            this._createEnabled(tpl, data)
            this._disable(true)
        },

        _setupEvents: function()
        {
           // To override
        },

        _enable: function(now) 
        { 
            var widget = this, dfd = new $.Deferred()
            var finish = function () { dfd.resolveWith(widget) }
            
            now = (now == null)? false : Boolean(now)
            this._show(this.element, (now)? false: this.options.show, finish)
            
            return dfd.promise()
        },

        _disable: function(now) 
        {
            var widget = this, dfd = new $.Deferred()
            var finish = function () { dfd.resolveWith(widget) }

            now = (now == null)? false : Boolean(now)
            this._hide(this.element, (now)? false: this.options.hide, finish)
            
            return dfd.promise()
        },

        _getTemplateVars: function() 
        { 
            var vars = $.extend({}, this.name)
            if (this.title) {
                vars.title = this.title
            }
            return vars
        },

        _extractTitle: function()
        {
            // Try to extract title from contained widget
            var title = null, 
                $header = this.$control.children('header')
            
            if ($header.length) {
               title = $header.children('h1,h2,h3,h4,h5').text()
            }
            return title
        },

        // Helpers

        _debug: function ()
        {
            var args1 = [].slice.call(arguments, 1),
                msg_prefix = this.widgetFullName
            console.debug.apply(console, 
                ['[%s] ' + arguments[0]].concat([msg_prefix], args1))
        },
    }) 
    
    $.widget('publicamundi.itemEditor', $.publicamundi.fieldwidget, {
        widgetEventPrefix: 'publicamundi-item_editor:',
        
        options: {
            placeholder: true,   // Use a placeholder when the widget is disabled
            allowDelete: true,   // Allow to delete this item (see onDelete)
            allowDisable: true,  // Allow to disable this item (possibly hidden, can be re-enabled)
            onDelete: 'self-destroy', // Choose: noop | self-destroy
            hasOrder: false,     // Whether this item participates in an ordered collection
            canMoveUp: false,    // Whether this item can be re-ordered by moving it one position 
                                 // towards the beginning, aka upwards (meaningfull only if hasOrder) 
            defaultTemplate: function (name) { 
                return 'script#' 
                    + name.namePrefix.replace(/[.]/g, '\\.') + '-item-template' 
            },
            editorCssClasses: {
                buttons: 'pull-right',
                enableBtn: 'pull-right',
            },
            editorTemplates: {
                btnSeparator: 
                    '<span class="btn-separator">{{content}}</span>',
                removeBtn:
                    '<a class="btn btn-mini {{removeActionClass}}" title="{{title}}">' + 
                       '<i class="icon-remove"></i>{{label}}</a>',
                removeBtnGroup:
                    '<div class="btn-group {{removeGroupClass}}">' +
                        '<a class="btn btn-mini {{disableActionClass}}" title="{{title}}">' + 
                            '<i class="icon-remove"></i>{{label}}</a>' +
                        '<a class="btn btn-mini dropdown-toggle" data-toggle="dropdown">' + 
                            '<span class="caret"></span></a>' +
                        '<ul class="dropdown-menu">' +
                            '<li>' + 
                                '<a class="btn-link btn-mini {{disableActionClass}}">{{disableLabel}}</a>' + 
                            '</li><li>' + 
                                '<a class="btn-link btn-mini {{removeActionClass}}">{{removeLabel}}</a>' + 
                            '</li>' +
                        '</ul>' +
                    '</div>',
                moveUpBtn:
                    '<a class="btn btn-mini {{moveUpActionClass}}" title="{{title}}">' + 
                        '<i class="icon-arrow-up"></i>{{label}}</a>', 
                enableBtn:
                    '<a class="btn btn-mini {{enableActionClass}}" title="{{title}}">' + 
                        '<i class="icon-pencil"></i>{{label}}</a>',
                placeholder:
                    '<h3 class="inline">{{title}}</h3>' + 
                    '<span class="label not-available">n/a</span>',
            },
            editorSelector: '.object-edit-widget',
        },
         
        _refresh: function()
        {
            var opts = this.options

            this._super()

            if (!opts.disabled && opts.hasOrder) {
                this.$control.find('header .item-actions .btn.move-up')
                    .attr('disabled', (opts.canMoveUp)? null : 'disabled')
            }

            return
        },

        _destroy: function()
        {
            // Empty everything 
            
            this.$control.remove()

            if (this.$placeholder) {
                this.$placeholder.remove()
            }

            this.$enableBtn.remove()
            this.$buttons.remove()

            this.element.empty()
        },
       
        _createEnabled: function (tpl, data)
        {
            var opts = this.options, $editor = null
            
            if (tpl) {
                // Generate from template
                this.$control = this._buildControlFromTemplate(tpl, data)
                this.element.empty().append(this.$control)
            } else {
                // The field-widget already exists, use it
                this.$control = this._queryControl()
            }

            this._buildAdditionalControls()
            if (this.$placeholder) {
                this.$placeholder.append(this.$enableBtn)
            }
   
            $editor = this.$control.children(opts.editorSelector)
            $editor.children('header').append(this.$buttons)
        },
        
        _createDisabled: function (tpl, data)
        {   
            var opts = this.options

            if (!opts.placeholder || !tpl) {
                // Prepare everything now
                this._createEnabled()
            } else {
                // We are going to use a placeholder to present a disabled editor.
                // Defer actual generation of the basic field-widget.
                
                this.element.empty()
                this.$control = $()
                
                this._buildAdditionalControls()
                this.$placeholder.append(this.$enableBtn)
                
                // Patch _enable in order to perform lazy generation
                
                var _enable = this._enable
                this._enable = function () {
                    // Generate  
                    this.$control = this._buildControlFromTemplate(tpl, data)
                    var $editor = this.$control.children(opts.editorSelector)
                    $editor.children('header').append(this.$buttons)

                    // Restore _enable and invoke immediately
                    this._enable = _enable
                    return this._enable()
                }
            }

            this._disable(true)
        },
        
        _buildAdditionalControls: function()
        {
            var opts = this.options,
                templates = opts.editorTemplates
            
            // Build button group for normal (enabled) mode 
            
            var $buttons = $('<div/>'), 
                $remove_btn = null,
                $move_btn = null,
                btn_separator = null
            
            btn_separator = render(templates.btnSeparator, { content: ' ' })

            if (!opts.allowDelete || !opts.allowDisable) {
                $remove_btn = $(render(templates.removeBtn, { 
                    label: 'Remove', 
                    title: (opts.allowDelete)? 'Discard this item' : 'Mark this item as not available',
                    removeActionClass: (opts.allowDelete)? 'remove delete' : 'remove disable',
                }))
            } else {
                $remove_btn = $(render(templates.removeBtnGroup, { 
                    label: 'Remove',
                    title: 'Remove (disable or discard) this item',
                    removeGroupClass: 'remove-opts',
                    disableLabel: 'Mark as not available',
                    disableActionClass: 'remove disable',
                    removeLabel: 'Discard this item', 
                    removeActionClass: 'remove delete',
                })) 
            }
            $buttons.prepend($remove_btn)
            
            if (opts.hasOrder) {
                $move_btn = $(render(templates.moveUpBtn, {
                    moveUpActionClass: 'move-up',
                    label: 'Up',
                    title: 'Move one position upwards',
                }))
                $buttons
                    .prepend($(btn_separator))
                    .prepend($move_btn)
            }
            
            this.$buttons = $buttons
                .addClass('item-actions')
                .addClass(opts.editorCssClasses.buttons)

            // Build buttons and placeholder for disabled mode

            var $enable_btn = null, 
                $placeholder = null

            $enable_btn = $(render(templates.enableBtn, { 
                label: 'Edit',
                title: '(Re)open this item and edit',
                enableActionClass: 'edit',
            }))
            this.$enableBtn = $enable_btn
                .addClass(opts.editorCssClasses.enableBtn)

            if (opts.placeholder) {
                $placeholder = $(render(templates.placeholder, { title: this.title }))
                $placeholder = $placeholder.appendTo($('<header/>')).parent()
            }
            this.$placeholder = $placeholder
        },

        _setupEvents: function()
        {
            var handle_edit, 
                handle_disable, 
                handle_delete,
                handle_move_up,
                handle_remove_hovered
            
            // Create handlers

            handle_remove_hovered = function (ev) {
                if (ev.type == 'mouseover') {
                    this.$control.addClass('remove-hover')
                } else if (ev.type == 'mouseout') {
                    this.$control.removeClass('remove-hover')
                }
                return false
            }
            
            handle_edit = this.enable

            handle_disable = this.disable
            
            handle_delete = function (ev) {
                switch (this.options.onDelete) {
                    case 'noop':
                        // Do nothing, a parent element will probably handle
                        break;
                    case 'self-destroy':
                    default:
                        // Start self-destruction using with the same effect as disable
                        var f = $.proxy(this.destroy, this)
                        this._hide(this.$control, this.options.hide, f)
                        break;
                }
                // Always trigger a `remove` event
                this._trigger(widget_events.Remove)
                return false
            }

            handle_move_up = function (ev) {
                this._trigger(widget_events.MoveUp)
                return false
            }

            // Bind handlers to this.element (delegated events)

            this._on(true, this.element, {
                'click header .edit': handle_edit,
            })

            this._on(false, this.element, {
                'click header .item-actions .remove.disable': handle_disable,
                'click header .item-actions .remove.delete': handle_delete,
                'click header .item-actions .move-up:enabled': handle_move_up,
                'mouseover header .item-actions > .remove': handle_remove_hovered,
                'mouseover header .item-actions > .remove-opts': handle_remove_hovered,
                'mouseout  header .item-actions > .remove': handle_remove_hovered,
                'mouseout  header .item-actions > .remove-opts': handle_remove_hovered,
            })
        },

        _enable: function(now)
        {
            var widget = this, 
                opts = this.options,
                dfd = new $.Deferred()
                
            var finish = function () { dfd.resolveWith(widget) }

            now = (now == null)? false : Boolean(now)

            if (this.$placeholder) {
                this.$placeholder.detach()
                this._hide(this.$control, false)
                this.element.append(this.$control)
                this._show(this.$control, (now)? false : opts.show, finish)
            } else {
                var $editor = this.$control.children(opts.editorSelector)
                var $header = $editor.children('header')
                this.$enableBtn.detach()
                this._hide(this.$buttons, false)
                $editor.find(':input').attr('disabled', null)
                $header.append(this.$buttons)
                this._show(this.$buttons, !now, finish)
            }

            return dfd.promise()
        },
       
        _disable: function(now)
        {
            var widget = this,
                opts = this.options,
                dfd = new $.Deferred()
                
            var finish = function () { dfd.resolveWith(widget) }

            now = (now == null)? false : Boolean(now)

            if (this.$placeholder) {
                this.$control.detach()
                this._hide(this.$placeholder, false)
                this.element.append(this.$placeholder)
                this._show(this.$placeholder, (now)? false : opts.show, finish)
            } else {
                var $editor = this.$control.children(opts.editorSelector)
                var $header = $editor.children('header')
                this.$buttons.detach()
                this._hide(this.$enableBtn, false)
                $editor.find(':input').attr('disabled', 'disabled')
                $header.append(this.$enableBtn)
                this._show(this.$enableBtn, !now, finish)
            }
            
            return dfd.promise()
        },

        _getTemplateVars: function() 
        { 
            var vars = this._super()
            return $.extend(vars, { key: this.name.nameKey })
        },

        _extractTitle: function()
        {
            var title = null,
                $editor = this.$control.children(this.options.editorSelector),
                $header = $editor.children('header')
            
            if ($header.length) {
               title = $header.children('h1,h2,h3,h4,h5').text()
            }
            return title
        },

        _checkSource: function (src)
        {
            var $src = null

            if (src instanceof $.publicamundi.itemEditor) {
                $src = src.element
            } else {
                $src = (src instanceof jQuery)? src.first() : $(src).first()
                src = $src.data(this.widgetFullName)
            }
            
            // Sanity checks
            
            if (!$src.length) {
                throw new Error('Cannot copy: empty element')
            } else if (!src) {
                throw new Error('Cannot copy: ' +
                    'source doesnt seem to be an publicamundi.itemEditor widget')
            } else if (src == this) { 
                throw new Error('Unwilling to copy: ' + 
                    'source is same as destination') 
            } else if (src.name.namePrefix != this.name.namePrefix) {
                throw new Error('Unwilling to copy: ' + 
                    'source item seems to belong to another collection')
            }
            
            return src
        },

        // Custom widget-specific methods
   
        copyValues: function (other)
        {
            // Copy input values from another instance of this widget
            
            var name_prefix = this.name.namePrefix,
                key = this.name.nameKey
            
            var src_widget = this._checkSource(other)
            var src_key = src_widget.name.nameKey
           
            var $input = this.element.find('[name]:input')

            src_widget.element.find('[name]:input').each(function (i, src) {
                var $src = $(src), $dst = null, name_path = null
                    
                name_path = $src.attr('name').substr(name_prefix.length).split('.')
                assert(name_path[0] == '' && name_path[1] == src_key)

                $dst = $input.filter(name_filter(
                    name_prefix + ['', key].concat(name_path.slice(2)).join('.')
                ))
                assert($dst.length > 0) 

                debug('Copying input from "%s" to "%s"', 
                    $src.attr('name'), $dst.attr('name'))
     
                if ($src.is('[type=checkbox]')) {
                    // Copy "checked" property
                    $dst.prop('checked', $src.prop('checked'))
                } else {
                    // Copy value
                    $dst.val($src.val())
                }
                
                $dst.trigger('change')
            })
        },
        
        swapValues: function (other)
        {
            // Swap input values with another instance of this widget
            
            var w1 = this,
                name_prefix = this.name.namePrefix,
                k1 = this.name.nameKey
            
            var w2 = this._checkSource(other)
            var k2 = w2.name.nameKey
           
            var $inp1 = w1.element.find('[name]:input')
            var $inp2 = w2.element.find('[name]:input')
            
            $inp1.each(function (i, x1) {
                var $x1 = $(x1), v1 = null, $x2 = null, name_path = null

                name_path = $x1.attr('name').substr(name_prefix.length).split('.')
                assert(name_path[0] == '' && name_path[1] == k1)

                $x2 = $inp2.filter(name_filter(
                    name_prefix + ['', k2].concat(name_path.slice(2)).join('.')
                ))
                assert($x2.length > 0) 
                
                debug('Swaping input between "%s" and "%s"', 
                    $x1.attr('name'), $x2.attr('name'))
                
                if ($x1.is('[type=checkbox]')) {
                    v1 = $x1.prop('checked')
                    $x1.prop('checked', $x2.prop('checked'))
                    $x2.prop('checked', v1)
                } else {
                    v1 = $x1.val()
                    $x1.val($x2.val())
                    $x2.val(v1)
                }

                $x1.trigger('change')
                $x2.trigger('change')
            })
        },

    })
});
