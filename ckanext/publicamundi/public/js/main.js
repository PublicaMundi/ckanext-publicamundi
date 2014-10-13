this.ckanext || (this.ckanext = {})
this.ckanext.publicamundi || (this.ckanext.publicamundi = {})

jQuery(document).ready(function ($) {
    
    var msg_prefix = '[publicamundi]'
    var console = window.console

    var debug = function () {
        console.debug.apply(console, [msg_prefix].concat(Array.slice(arguments)))
    }
    var error = $.proxy(console, 'error')
    var warn = $.proxy(console, 'warn')
    var assert = $.proxy(console, 'assert')
   
    var Name = function (qname) {
        var i = qname.toString().lastIndexOf('.')
        this.qname = qname
        this.namePrefix = (i > 0)? qname.substring(0, i) : null
        this.nameKey = (i > 0)? qname.substring(i + 1) : qname
    }
    
    Name.parse = function (qname) { return new Name(qname) }

    var FieldWidget = $.inherit(Object, 
        // Define instance (prototype) properties
        {
            name: null,
            _isAttached: null,
            _isPrepared: false,
            constructor: function (qname, $el, $parent) 
            {
                this.name = Name.parse(qname)
                this.$el = $el
                
                if ($parent) {
                    this.$parent = $parent
                    this._isAttached = false
                } else {
                    $parent = $el.parent()
                    if ($parent.length) {
                        this.$parent = $parent
                        this._isAttached = true
                    } else {
                        throw new Error('Cannot create a widget without a parent!')
                    }
                }
            },
            prepare: function () 
            {
                if (!this._isPrepared) {
                    this._prepareOnce()
                    this._isPrepared = true
                }
            },
            render: function (show) 
            {
                show = (show == null)? true : Boolean(show)
                if (show) {
                    this.$el.fadeIn()
                } else {
                    this.$el.fadeOut()
                }
            },
            _prepareOnce: function()
            {
                if (!this._isAttached) {
                    this.$el.hide()
                    this.$parent.append(this.$el)
                }
            }
        },
        // Define static properties
        {
            clsPrefix: 'field-qname-',
            createFromElement: function ($el) 
            {
                var ctor = this, qname = null, widget = null
                qname = $el.attr('class').split(' ')
                    .filter(function (a) { return a.startsWith(ctor.clsPrefix) })
                if (qname.length > 0) {
                    qname = qname.pop().substring(ctor.clsPrefix.length) 
                    widget = new ctor(qname, $el)
                }    
                return widget
            },
            createFromName: function (qname) 
            {
                var ctor = this, widget = null
                var selector = '.widget' + ('.' + ctor.clsPrefix + qname.replace(/[.]/g, '\\.'))
                var $el = $(selector).first()
                if ($el.length > 0) {
                    widget = new ctor(qname, $el)
                }
                return widget
            },
            createFromTemplate: function (tpl, $parent, qname, data) 
            {
                var ctor = this, widget = null, $el = null
                
                // Override data (via prototype) and render template
                data = Object.create(data)
                data.qname = qname
                $el = $(Mustache.render(tpl, data))
                
                // Verify proper classes exist
                assert($el.hasClass('field-widget'))
                assert($el.hasClass(ctor.clsPrefix + qname)) 
                
                // Create widget
                widget = new ctor(qname, $el, $parent)
                return widget
            }, 
            createFromTemplateScript: function ($tpl, $parent, qname, data)
            {
                var ctor = this, tpl = null
                if (!($tpl instanceof jQuery)) {
                    $tpl = $('script#' 
                        + qname.replace(/[.]/g, '\\.') + '-template')
                }
                if (!$tpl.length) {
                    return null
                } else {
                    tpl = $tpl.text()
                    return ctor.createFromTemplate(tpl, $parent, qname, data)
                }
            },
        }
    );
    
    var ContainerItemEditor = $.inherit(FieldWidget, 
        {
            constructor: function (qname, $el, $parent) {
                FieldWidget.call(this, qname, $el, $parent)
            }, 
        },
        {
            createFromTemplate: function (tpl, $parent, qname, data) 
            {
                var ctor = this, parent_ctor = FieldWidget
                qname = Name.parse(qname)
                data = Object.create(data)
                data.key = qname.nameKey
                return parent_ctor.createFromTemplate.call(ctor, tpl, $parent, qname.qname, data) 
            },            
            createFromTemplateScript: function ($tpl, $parent, qname, data)
            {
                var ctor = this, parent_ctor = FieldWidget, tpl = null
                qname = Name.parse(qname)
                data = Object.create(data)
                data.key = qname.nameKey
                if (!($tpl instanceof jQuery)) {
                    $tpl = $('script#' 
                        + qname.namePrefix.replace(/[.]/g, '\\.') + '-item-template')
                }
                if (!$tpl.length) {
                    return null
                } else {
                    tpl = $tpl.text()
                    return parent_ctor.createFromTemplate.call(ctor, tpl, $parent, qname.qname, data)
                }
            },
        }
    );
    
    var ListItemEditor = $.inherit(ContainerItemEditor, 
        {
            // Todo
        },
        {
            // Todo
        }
    );
    
    var DictItemEditor = $.inherit(ContainerItemEditor, 
        {
            render: function (show) 
            {
                show = (show == null)? true : Boolean(show)

                if (show) {
                    // ..
                } else {
                    // ..
                }
            },
            _prepareOnce: function () 
            {
                // Add a "remove" button, re-style header
                
                var widget = this, ctor = this.constructor
                var $w1 = widget.$el.children('.object-edit-widget')
                var $header = $w1.children('header')
            
                var $remove_btn = $(Mustache.render(
                    ctor.templates['remove-btn'], { label: 'Remove' }))
                $remove_btn
                    .on('click', function () {
                        widget.render(false)
                    })
                    .on('mouseover', function () { 
                        widget.$el.css({'background-color': '#f7f7f7',})
                    }) 
                    .on('mouseout', function () { 
                        widget.$el.css({'background-color':'inherit',}) 
                    }) 
                
                $header.children('h3').addClass('inline')
                $header.append($remove_btn)
                
                // Create a placeholder widget

                // Todo
            },
        },
        {
            options: {
                showPlaceholder: true,
            },
            templates: {
                'remove-btn': 
                    '<a class="btn btn-small pull-right remove-object" title="{{title}}"><i class="icon-remove"></i> {{label}}</a>',
                'edit-btn':
                    '<a class="btn btn-small pull-right edit-object" title="{{title}}"><i class="icon-pencil"></i> {{label}}</a>',
                'placeholder-widget':
                    '<header><h3 class="inline">{{title}}</h3><span class="label not-available">n/a</span> {{{edit-btn}}}</header>',
            },
        }
    );

    $.extend(ckanext.publicamundi, {
        FieldWidget: FieldWidget,
        ListItemEditor: ListItemEditor,
        DictItemEditor: DictItemEditor,
    })
});

