
jQuery(document).ready(function ($) {
    
    var console = window.console

    var debug = $.proxy(console, 'debug') 
    var warn = $.proxy(console, 'warn')
    var error = $.proxy(console, 'error')
    var assert = $.proxy(console, 'assert')
    
    var render = Mustache.render 

    var parseName = function (qname) {
        var i = qname.lastIndexOf('.')
        return {
            qname: qname,
            namePrefix: (i > 0)? qname.substring(0, i) : null,
            nameKey: (i > 0)? qname.substring(i + 1) : qname,
        }
    }

    $.widget('publicamundi.fieldwidget', {
        options: {
            qname: null,
            title: null,
            template: null,
            defaultTemplate: function (name) {
                return 'script#' + name.qname.replace(/[.]/g, '\\.') + '-template' 
            },
            classPrefix: 'field-qname-',
            hide: { duration: 400, },
            show: { duration: 400, easing: 'swing' },
        },

        _create: function()
        {
            var opts = this.options, tpl = null, dat = null
            
            this.name = parseName(opts.qname)
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
            
            // Create in the requested (enabled/disabled) mode, fire the proper events

            if (opts.disabled) {
                this._createDisabled(tpl, dat)
                this._trigger('created')
                this._trigger('disabled')
            } else {
                this._createEnabled(tpl, dat)
                this._trigger('created')
                this._trigger('enabled')
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
            // Note: It will delegate to _destroy() for widget-specific cleanup
            this._super()
            // When finished, fire a proper event
            this._trigger('destroyed')
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
            if (this.options.disabled) {
                this._enable()
                this.options.disabled = false
                this._trigger('enabled')
            }
        },
       
        disable: function()
        {
            if (!this.options.disabled) {
                this._disable()
                this.options.disabled = true
                this._trigger('disabled')
            }
        },

        // Base implementation

        _generateControlFromTemplate: function (tpl, data)
        {
            var $w = null

            $.extend(data, this._getTemplateVars())
            $w = $(render(tpl, data))
            
            assert($w.hasClass('field-widget'))
            assert($w.hasClass(this.options.classPrefix + this.name.qname))

            return $w
        },

        _queryControl: function ()
        {
            var qname = this.name.qname, opts = this.options, $w = null
            var selector = '.field-widget'
                + ('.' + opts.classPrefix + qname.replace(/[.]/g, '\\.'))
            
            $w = this.element.children(selector)
            assert($w.length == 1)

            return $w
        },

        _createEnabled: function (tpl, data)
        {
            if (tpl) {
                // Generate from template
                this.$widget = this._generateControlFromTemplate(tpl, data)
                this.element.empty().append(this.$widget)
            } else {
                // The field-widget already exists, use it
                this.$widget = this._queryControl()
            }
        },
        
        _createDisabled: function (tpl, data)
        {
            // In this base implementation, we just create our widget in enabled mode,
            // and then we immediately disable it. But, a derived widget may choose to
            // do different things (such as to lazily load actual this.$widget when this
            // is really needed).
            
            this._createEnabled(tpl, data)
            this._disable()
        },

        _setupEvents: function()
        {
            $.noop() // Override
        },

        _enable: function() 
        { 
            this._show(this.element, this.options.show)
        },

        _disable: function() 
        { 
            this._hide(this.element, this.options.hide)
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
            var title = null 
            var $header = this.$widget.children('header')
            if ($header.length) {
               title = $header.children('h1,h2,h3,h4,h5').text()
            }
            return title
        },
    }) 
    
    $.widget('publicamundi.itemEditor', $.publicamundi.fieldwidget, {
        widgetEventPrefix: 'publicamundi-item_editor-',
        
        options: {
            placeholder: true, // Whether to use a placeholder when widget is disabled
            allowDelete: false, // Whether user is allowed to delete this item (and destroy the widget)
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
                    '<button class="btn btn-small {{removeActionClass}}"><i class="icon-remove"></i> {{label}}</button>',
                removeBtnGroup:
                    '<div class="btn-group {{removeGroupClass}}">' +
                        '<button class="btn btn-small {{removeActionClass}}"><i class="icon-remove"></i> {{label}}</button>' +
                        '<button class="btn btn-small dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>' +
                        '<ul class="dropdown-menu">' +
                            '<li><a class="btn-small {{removeActionClass}}">{{removeLabel}}</a></li>' +
                            '<li><a class="btn-small {{deleteActionClass}}">{{deleteLabel}}</a></li>' +
                        '</ul>' +
                    '</div>',
                editBtn:
                    '<button class="btn btn-small {{editActionClass}}"><i class="icon-pencil"></i> {{label}}</button>',
                placeholder:
                    '<h3 class="inline">{{title}}</h3><span class="label not-available">n/a</span>',
            },
            editorSelector: '.object-edit-widget',
        },
         
        _destroy: function()
        {
            // Empty everything 
            
            this.$widget.remove()

            if (this.$placeholder) {
                this.$placeholder.remove()
            }

            this.$editBtn.remove()
            this.$removeBtn.remove()

            this.element.empty()
        },
       
        _createEnabled: function (tpl, data)
        {
            var opts = this.options, $w, $editor
            
            if (tpl) {
                // Generate from template
                this.$widget = this._generateControlFromTemplate(tpl, data)
                this.element.empty().append(this.$widget)
            } else {
                // The field-widget already exists, use it
                this.$widget = this._queryControl()
            }

            this._generateAdditionalControls()
            if (this.$placeholder) {
                this.$placeholder.append(this.$editBtn)
            }
   
            $editor = this.$widget.children(opts.editorSelector)
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
                this.$widget = $()
                
                this._generateAdditionalControls()
                this.$placeholder.append(this.$editBtn)
                
                // Patch _enable in order to perform lazy generation
                
                var _enable = this._enable
                this._enable = function () {
                    // Generate  
                    this.$widget = this._generateControlFromTemplate(tpl, data)
                    var $editor = this.$widget.children(this.options.editorSelector)
                    $editor.children('header').append(this.$removeBtn)

                    // Restore _enable and invoke immediately
                    this._enable = _enable
                    this._enable()
                }
            }

            this._disable()
        },
        
        _generateAdditionalControls: function()
        {
            var opts = this.options,
                css_classes = opts.editorCssClasses,
                templates = opts.editorTemplates,
                $remove_btn = null, 
                $edit_btn = null, 
                $placeholder = null
            
            if (!opts.allowDelete) {
                $remove_btn = $(render(templates.removeBtn, { 
                    label: 'Remove', 
                    removeActionClass: 'remove' 
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
            var handle_remove_hover = function (ev) {
                if (ev.type == 'mouseover') {
                    this.$widget.css({ 'background-color': '#f7f7f7' })
                } else if (ev.type == 'mouseout') {
                    this.$widget.css({ 'background-color': 'inherit' })
                }
                return false
            }
        
            // Bind event handlers
            
            this._on(true, this.element, {
                'click header .edit': this.enable,
            })

            this._on(false, this.element, {
                'click header .remove': this.disable,
                'click header .delete': this.destroy,
                'mouseover header button.remove': handle_remove_hover,
                'mouseout  header button.remove': handle_remove_hover,
            })
        },

        _enable: function()
        {
            var opts = this.options 

            if (this.$placeholder) {
                this.$placeholder.detach()
                this.$widget.hide()
                this.element.append(this.$widget)
                this.$widget.fadeIn(opts.show)
            } else {
                var $editor = this.$widget.children(opts.editorSelector)
                var $header = $editor.children('header')
                this.$editBtn.detach()
                this.$removeBtn.hide()
                $editor.find(':input').attr('disabled', null)
                $header.append(this.$removeBtn)
                this.$removeBtn.fadeIn(opts.show)
            }
        },
       
        _disable: function()
        {
            var opts = this.options
            
            if (this.$placeholder) {
                this.$widget.detach()
                this.$placeholder.hide()
                this.element.append(this.$placeholder)
                this.$placeholder.fadeIn(opts.show)
            } else {
                var $editor = this.$widget.children(opts.editorSelector)
                var $header = $editor.children('header')
                this.$removeBtn.detach()
                this.$editBtn.hide()
                $editor.find(':input').attr('disabled', 'disabled')
                $header.append(this.$editBtn)
                this.$editBtn.fadeIn(opts.show)
            }
        },

        _getTemplateVars: function() 
        { 
            var vars = this._super()
            return $.extend(vars, { key: this.name.nameKey })
        },

        _extractTitle: function()
        {
            var title = null,
                $w1 = this.$widget.children(this.options.editorSelector),
                $header = $w1.children('header')
            
            if ($header.length) {
               title = $header.children('h1,h2,h3,h4,h5').text()
            }
            return title
        },

    })
});

