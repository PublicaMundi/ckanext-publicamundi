
jQuery(document).ready(function ($) {
    
    var console = window.console
        debug = $.proxy(console, 'debug') 
        warn = $.proxy(console, 'warn')
        error = $.proxy(console, 'error')
        assert = $.proxy(console, 'assert')

    var render = Mustache.render 
    
    // Enumerate events emitted by following widgets
    var widget_events = {
        Create: 'create',
        Destroy: 'destroy',
        Enable: 'enable',
        Disable: 'disable',
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

        _generateControlFromTemplate: function (tpl, data)
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
                this.$control = this._generateControlFromTemplate(tpl, data)
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
            placeholder: true, // Use a placeholder when the widget is disabled
            allowDelete: true, // Allow to delete this item (self-destroys the widget)
            allowRemove: true, // Allow to remove this item (disables the widget, can be re-enabled)
            defaultTemplate: function (name) { 
                return 'script#' 
                    + name.namePrefix.replace(/[.]/g, '\\.') + '-item-template' 
            },
            editorCssClasses: {
                removeBtn: 'pull-right',
                removeBtnGroup: 'pull-right',
                editBtn: 'pull-right',
            },
            editorTemplates: {
                removeBtn:
                    '<button class="btn btn-small {{removeActionClass}}">' + 
                       '<i class="icon-remove"></i> {{label}}</button>',
                removeBtnGroup:
                    '<div class="btn-group {{removeGroupClass}}">' +
                        '<button class="btn btn-small {{removeActionClass}}">' + 
                            '<i class="icon-remove"></i> {{label}}</button>' +
                        '<button class="btn btn-small dropdown-toggle" data-toggle="dropdown">' + 
                            '<span class="caret"></span></button>' +
                        '<ul class="dropdown-menu">' +
                            '<li>' + 
                                '<a class="btn-link btn-small {{removeActionClass}}">{{removeLabel}}</a>' + 
                            '</li><li>' + 
                                '<a class="btn-link btn-small {{deleteActionClass}}">{{deleteLabel}}</a>' + 
                            '</li>' +
                        '</ul>' +
                    '</div>',
                editBtn:
                    '<button class="btn btn-small {{editActionClass}}">' + 
                        '<i class="icon-pencil"></i> {{label}}</button>',
                placeholder:
                    '<h3 class="inline">{{title}}</h3>' + 
                    '<span class="label not-available">n/a</span>',
            },
            editorSelector: '.object-edit-widget',
        },
         
        _destroy: function()
        {
            // Empty everything 
            
            this.$control.remove()

            if (this.$placeholder) {
                this.$placeholder.remove()
            }

            this.$editBtn.remove()
            this.$removeBtn.remove()

            this.element.empty()
        },
       
        _createEnabled: function (tpl, data)
        {
            var opts = this.options, $editor = null
            
            if (tpl) {
                // Generate from template
                this.$control = this._generateControlFromTemplate(tpl, data)
                this.element.empty().append(this.$control)
            } else {
                // The field-widget already exists, use it
                this.$control = this._queryControl()
            }

            this._generateAdditionalControls()
            if (this.$placeholder) {
                this.$placeholder.append(this.$editBtn)
            }
   
            $editor = this.$control.children(opts.editorSelector)
            $editor.children('header').append(this.$removeBtn)
        },
        
        _createDisabled: function (tpl, data)
        {   
            if (!this.options.placeholder || !tpl) {
                // Prepare everything now
                this._createEnabled()
           } else {
                // We are going to use a placeholder to present a disabled editor.
                // Defer actual generation of the basic field-widget.
                
                this.element.empty()
                this.$control = $()
                
                this._generateAdditionalControls()
                this.$placeholder.append(this.$editBtn)
                
                // Patch _enable in order to perform lazy generation
                
                var _enable = this._enable
                this._enable = function () {
                    // Generate  
                    this.$control = this._generateControlFromTemplate(tpl, data)
                    var $editor = this.$control.children(this.options.editorSelector)
                    $editor.children('header').append(this.$removeBtn)

                    // Restore _enable and invoke immediately
                    this._enable = _enable
                    return this._enable()
                }
            }

            this._disable(true)
        },
        
        _generateAdditionalControls: function()
        {
            var opts = this.options,
                css_classes = opts.editorCssClasses,
                templates = opts.editorTemplates,
                $remove_btn = null, 
                $edit_btn = null, 
                $placeholder = null
            
            if (!opts.allowDelete || !opts.allowRemove) {
                $remove_btn = $(render(templates.removeBtn, { 
                    label: 'Remove', 
                    removeActionClass: (opts.allowDelete)? 'delete' : 'remove'
                }))
                $remove_btn.addClass(css_classes.removeBtn)
            } else {
                $remove_btn = $(render(templates.removeBtnGroup, { 
                    label: 'Remove',
                    removeGroupClass: 'remove-opts',
                    removeLabel: 'Mark as not available',
                    removeActionClass: 'remove',
                    deleteLabel: 'Remove the item entirely', 
                    deleteActionClass: 'delete', 
                })) 
                $remove_btn.addClass(css_classes.removeBtnGroup)
            }
            this.$removeBtn = $remove_btn
            
            $edit_btn = $(render(templates.editBtn, { 
                label: 'Edit', 
                editActionClass: 'edit' }))
            $edit_btn.addClass(css_classes.editBtn)
            this.$editBtn = $edit_btn
            
            if (this.options.placeholder) {
                $placeholder = $(render(templates.placeholder, { title: this.title }))
                $placeholder = $placeholder.appendTo($('<header/>')).parent()
            }
            this.$placeholder = $placeholder
        },

        _setupEvents: function()
        {
            var handle_edit, 
                handle_remove, 
                handle_delete, 
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

            handle_remove = this.disable
            
            handle_delete = function () {
                // Start self-destroy using with the same effect as disable
                var f = function () { this.destroy() }
                this._hide(this.$control, this.options.hide, $.proxy(f, this))
            }

            // Bind handlers to this.element (delegated events)

            this._on(true, this.element, {
                'click header .edit': handle_edit,
            })

            this._on(false, this.element, {
                'click header .remove': handle_remove,
                'click header .delete': handle_delete,
                'mouseover header button.remove': handle_remove_hovered,
                'mouseout  header button.remove': handle_remove_hovered,
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
                this.$editBtn.detach()
                this._hide(this.$removeBtn, false)
                $editor.find(':input').attr('disabled', null)
                $header.append(this.$removeBtn)
                this._show(this.$removeBtn, !now, finish)
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
                this.$removeBtn.detach()
                this._hide(this.$editBtn, false)
                $editor.find(':input').attr('disabled', 'disabled')
                $header.append(this.$editBtn)
                this._show(this.$editBtn, !now, finish)
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
            
            var widget = this,
                name_prefix = this.name.namePrefix,
                key = this.name.nameKey
            
            var other_widget = this._checkSource(other)
            var other_key = other_widget.name.nameKey
           
            var $input = this.element.find('[name]:input')
            
            // Todo
        },

    })
});
