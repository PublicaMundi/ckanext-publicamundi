(function () {

    var debug = $.proxy(window.console, 'debug')
    var warn = $.proxy(window.console, 'warn')
    
    this.ckan.module('resource-metadata', function ($, _) {

        return {
            options: {
            },

            initialize: function () 
            {
                var module = this,
                    $el = this.el,
                    opts = this.options;
                
                if (!$el.is('form')) {
                    warn('Expected a form element');
                    return;
                }
                
                module.dirty = false

                $el.on('change.resource-metadata', 'input[name=url]', function (ev) {
                    module.dirty = true
                })

                $el.on('submit.resource-metadata', function (ev) {
                    var url = $el.find('input[name=url]').val();
                    var $upload = $el.find('input[name=upload]:eq(0)');
                    var files = $upload.prop('files')
                    if (url.length == 0 && files.length > 0) {
                        var f = files.item(0),
                            $div = $el.find('.hidden-fields');
                        $div.find('input[name=size]').val(f.size.toString());
                        $div.find('input[name=last_modified]').val(moment(f.lastModifiedDate).format('YYYY-MM-DD'));
                        $div.find('input[name=mimetype]').val(f.type.toString());
                    } else if (module.dirty) {
                        $el.find('.hidden-fields input').val('');
                    } 
                });

                debug('Initialized module: resource-metadata opts=', opts);
            },

            teardown: function () 
            { 
                this.el.off('submit.resource-metadata');
                this.el.off('change.resource-metadata');
                debug('Tearing down module: resource-metadata');
            },
        };
    });

}).apply(this);
