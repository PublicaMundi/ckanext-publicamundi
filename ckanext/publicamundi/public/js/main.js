this.ckanext || (this.ckanext = {})
this.ckanext.publicamundi || (this.ckanext.publicamundi = {})

jQuery(document).ready(function ($) {
    
    var console = window.console
    var debug = $.proxy(console, 'debug') 
    var warn = $.proxy(console, 'warn')
    var error = $.proxy(console, 'error')
    var assert = $.proxy(console, 'assert')
   
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
            var opts = this.options
            
            this.name = parseName(opts.qname)
            this.title = opts.title
            
            if (opts.template) {
                // The field widget doesnt exist: must be created from a template 
                var $w = null, tpl = null, dat = null
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
                // Render template and verify result
                $.extend(dat, this._getTemplateVars())
                $w = $(Mustache.render(tpl, dat))
                assert($w.hasClass('field-widget'))
                assert($w.hasClass(opts.classPrefix + this.name.qname))
                // Attach to container element
                this.element.empty().append($w)
                this.$widget = $w
            } else {
                // The field widget allready exists
                var selector = '.widget' 
                    + ('.' + opts.classPrefix + this.name.qname.replace(/[.]/g, '\\.'))
                this.$widget = this.element.children(selector)
                assert(this.$widget.length == 1) 
            }
            
            if (!this.title) {
                this.title = this._extractTitle()
            }

            // If created at disabled mode, disable it. Fire the appropriate
            // events in any case.
            
            this._trigger('created')
            
            if (opts.disabled) {
                this._disable()
                this._trigger('disabled')
                debug('Created widget "' + this.widgetFullName + '" at disabled mode')
            } else { 
                this._trigger('enabled')
            }

            // Done

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

        // Implementation

        _enable: function() 
        { 
            this._show(this.element, this.options.show)
            //this.element.show(this.options.show)
        },

        _disable: function() 
        { 
            this._hide(this.element, this.options.hide)
            //this.element.hide(this.options.hide)    
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
    
    $.widget('publicamundi._itemEditor', $.publicamundi.fieldwidget, {
        options: {
            defaultTemplate: function (name) { 
                return 'script#' 
                    + name.namePrefix.replace(/[.]/g, '\\.') + '-item-template' 
            }
        },
        
        _destroy: function()
        {
            // Empty everything, even if not created from template
            this.element.empty()
        },

        _enable: function()
        {
            this.$widget.find(':input').attr('disabled', null)
        },
       
        _disable: function()
        {
            this.$widget.find(':input').attr('disabled', 'disabled') 
        },
       
        _getTemplateVars: function() 
        { 
            var vars = this._super()
            return $.extend(vars, { key: this.name.nameKey })
        },

        _extractTitle: function()
        {
            var title = null 
            var $w1 = this.$widget.children('.object-edit-widget')
            var $header = $w1.children('header')
            if ($header.length) {
               title = $header.children('h1,h2,h3,h4,h5').text()
            }
            return title
        },

    })
   
    $.widget('publicamundi.itemEditor', $.publicamundi._itemEditor, {
        widgetEventPrefix: 'publicamundi-item_editor-',
        
        options: {
            placeholder: true, // Use a placeholder when detached (disabled mode)
            editorTemplates: {
                removeBtn:
                    '<a class="btn btn-small pull-right" title="{{title}}"><i class="icon-remove"></i> {{label}}</a>',
                editBtn:
                    '<a class="btn btn-small pull-right" title="{{title}}"><i class="icon-pencil"></i> {{label}}</a>',
                placeholder:
                    '<h3 class="inline">{{title}}</h3><span class="label not-available">n/a</span>',
            },
        },

        _create: function()
        {
            this._super()
            this._prepareEditor()
        },
        
        _prepareEditor: function()
        {
            // Add a "remove" button, re-style header
                
            var templates = this.options.editorTemplates, $widget = this.$widget
            var $remove_btn, $edit_btn, $p, remove_handler, edit_handler
            
            var $w1 = $widget.children('.object-edit-widget')
            var $header = $w1.children('header')

            $remove_btn = $(Mustache.render(templates.removeBtn, { label: 'Remove' }))
            $remove_btn.addClass('remove-object')
            
            $header.children('h3').addClass('inline')
            $header.append($remove_btn)
            
            $edit_btn = $(Mustache.render(templates.editBtn, { label: 'Edit' }))
            $edit_btn.addClass('edit-object')
                       
            if (this.options.placeholder) {
                // Create a placeholder element, setup enable/disable handlers
                $p = $(Mustache.render(templates.placeholder, { title: this.title }))
                $p = $p.appendTo($('<header/>')).parent()
                this.$placeholder = $p.append($edit_btn)    
                edit_handler = function () { this.enable() }
                remove_handler = function () { this.disable() }
            } else {
                // No placeholder, just setup enable/disable handlers
                edit_handler = function () { 
                    this.enable()
                    $edit_btn.detach()
                    $header.append($remove_btn)
                } 
                remove_handler = function () { 
                    this.disable()
                    $remove_btn.detach()
                    $header.append($edit_btn)
                }
            }

            // Bind event handlers
                 
            this._on(true, this.element, {
                'click header > .edit-object': edit_handler
            })

            this._on(false, this.element, {
                'click header > .remove-object': remove_handler
            })

            this._on(false, this.element, {
                'mouseover header > .remove-object': function () {
                    this.$widget.css({'background-color': '#f7f7f7',})
                },
                'mouseout header > .remove-object': function () {
                    this.$widget.css({'background-color': 'inherit',})
                }, 
            })

            return
        },

        _enable: function()
        {
            if (this.options.placeholder) {
                this.$placeholder.detach()
                this.$widget.hide()
                this.element.append(this.$widget)
                this.$widget.fadeIn(this.options.show)
            } else {
                this.$widget.find(':input').attr('disabled', null)
            }
        },
       
        _disable: function()
        {
            if (this.options.placeholder) {
                this.$widget.detach()
                this.$placeholder.hide()
                this.element.append(this.$placeholder)
                this.$placeholder.fadeIn(this.options.show)
            } else {
                this.$widget.find(':input').attr('disabled', 'disabled')
            }
        },
    })
    
});

