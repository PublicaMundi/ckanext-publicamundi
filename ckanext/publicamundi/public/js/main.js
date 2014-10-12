this.ckanext || (this.ckanext = {})
this.ckanext.publicamundi || (this.ckanext.publicamundi = {})

jQuery(document).ready(function ($) {
    
    var debug_prefix = '[publicamundi]'

    var debug = function () {
        var console = window.console
        var args = [].concat([debug_prefix], Array.slice(arguments))
        console.debug.apply(console, args)
    }
   
    var Name = function (qname) {
        var i = qname.toString().lastIndexOf('.')
        this.qname = qname
        this.namePrefix = (i > 0)? qname.substring(0, i) : null
        this.nameKey = (i > 0)? qname.substring(i + 1) : qname
    }

    var BaseWidget = $.inherit(Object, 
        // Define instance (prototype) properties
        {
            qname: null,
            selector: null,
            constructor: function (qname) 
            {
                debug('BaseWidget: Ctor ...')
                this.qname = new Name(qname)
                this.selector = '.widget' + 
                    ('.' + this.constructor.clsPrefix + qname.replace(/[.]/g, '\\.'))
            },
            prepare: function () 
            {
                debug('Prepare ...')
            },
            render: function () 
            {
                debug('Render ...')
            },
        },
        // Define static properties
        {
            clsPrefix: 'field-qname-',
            createFromElement: function ($el) 
            {
                var ctor = this
                var qname = $el.attr('class').split(' ')
                    .filter(function (a) { return a.startsWith(ctor.clsPrefix) })
                    .pop().substring(ctor.clsPrefix.length) 
                return this.createFromName(qname)
            },
            createFromName: function (qname) 
            {
                var ctor = this
                var widget = new ctor(qname)
                return widget
            },
            createFromTemplate: function (tpl, name, data) 
            {
                
            }, 
        }
    );

    var ListItemEditor = $.inherit(BaseWidget, 
        {
            constructor: function (qname) {
                debug('ListItemEditor: Ctor ...')
                BaseWidget.call(this, qname)
            }, 
        },
        {
        }
    );

    $.extend(ckanext.publicamundi, {
        Name: Name,
        BaseWidget: BaseWidget,
        ListItemEditor: ListItemEditor,
        //DictItemEditor: DictItemEditor,
    })
});

