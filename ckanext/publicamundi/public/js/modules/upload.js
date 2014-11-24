/* Fixme 
 * Rewrite basic part as a jQuery-Ui widget.
 */

(function () {

    var debug = $.proxy(window.console, 'debug');
    var info = $.proxy(window.console, 'info');
    var warn = $.proxy(window.console, 'warn');
    var assert = $.proxy(window.console, 'assert');

    var render = Mustache.render;

    this.ckan.module('upload-link', function ($, _) {

        return {
            options: {
                name: null,
                eventPrefix: 'upload-link:',
            },

            templates: {
                selectedFile: '{{name}} <code>({{size}})</code>',
            },

            initialize: function () 
            {
                var module = this,
                    $el = this.el,
                    opts = this.options,
                    templates = this.templates;
 
                $el.find('.controls.choose-method input[type=file]')
                    .css('width', $('button.upload-file').outerWidth())
                    .on('change', function (ev) {
                        var fileobj = this.files.item(0)
                        debug('A file was selected:', fileobj.name)
                        $el.find('.selected-file')
                            .html(module._summarizeSelectedFile(fileobj))
                        $el.children('.controls.choose-method').hide();
                        $el.children('.controls.upload-file').show();
                        return true;
                    })
                    .show();
                    
                $el.find('.controls.choose-method button.upload-file')
                    .on('click', function () {
                        warn('This click should have been intercepted by input:file!')
                        return false;
                    })
                
                $el.find('.controls.choose-method button.link-file')
                    .on('click', function () { 
                        $el.children('.controls.choose-method').hide();
                        $el.children('.controls.link-file').show();
                        return false; 
                    })
                 
                $el.find('.controls.link-file button.remove-link')
                    .on('click', $.proxy(module._discardLink, module));

                $el.find('.controls.upload-file button.remove-file')
                    .on('click', $.proxy(module._discardUpload, module));
                
                // The following events are specific to upload-ajax.html

                $el.find('.controls.link-file button.proceed')
                    .on('click', $.proxy(module._proceedWithLink, module));
                
                $el.find('.controls.upload-file button.proceed')
                    .on('click', $.proxy(module._proceedWithUpload, module));
                
                $el.find('.controls.link-file input[type=url]')
                    .on('keypress, change', $.proxy(module._validateLink, module));
                module._validateLink();

                debug('Initialized module: upload-link opts=', opts);
            },

            teardown: function () 
            { 
                debug('Tearing down module: upload-link')
            },
            
            _refreshLoadingButton: function ($btn, loading)
            {
                var module = this;

                var $icon = $btn.children('i');
                
                // Save icon's original class (in order to restore it)
                
                if (!$icon.data('original-class')) { 
                    $icon.data('original-class', $icon.attr('class'));
                }
                
                // Display a delayed "loading" effect
                
                var tid = $btn.data('start-loading');
                if (loading) {
                    if (!tid) {
                        tid = window.setTimeout(function () {
                            $icon.attr('class', 'icon-refresh icon-spin');
                            $btn.attr('disabled', 'disabled');
                            $btn.data('start-loading', null);
                        }, 500);
                        $btn.data('start-loading', tid);
                    }
                } else {
                    if (tid) {
                        window.clearTimeout(tid);
                        $btn.data('start-loading', null);
                    }
                    $icon.attr('class', $icon.data('original-class'));
                    $btn.attr('disabled', null);
                }

                return;
            },

            _formatSize: function (size)
            {
                var units = ['B', 'KB', 'MB', 'GB'];
                var n = Math.floor(Math.log(size) / Math.log(1024)),
                    a = size / Math.pow(1024, n);
                return a.toFixed(1) + ' ' + units[n];
            },

            _summarizeSelectedFile: function (fileobj) 
            {
                var module = this;
                
                var vars = {
                    name: fileobj.name,
                    size: module._formatSize(fileobj.size),
                    mimetype: fileobj.type,
                }

                return render(module.templates.selectedFile, vars);
            },
           
            _validateLink: function ()
            {
                var module = this, $el = this.el;
                
                var $link = $el.find('.controls.link-file input[type=url]');
                
                // Check validity

                var valid = ($link.val().length > 0);
                if (valid && $link.prop('validity')) {
                    // Use native validation (if available)
                    valid = $link.prop('validity').valid;
                }
                
                // Toggle enable/disable on proceed button
                
                $el.find('.controls.link-file button.proceed')
                    .attr('disabled', (valid) ? null : 'disable');
                
                return true;
            },

            _discardLink: function () 
            {
                var module = this, $el = this.el;
                
                var $link = $el.find('.controls.link-file input[type=url]');

                $el.children('.controls.link-file').hide();
                $el.children('.controls.choose-method').show();
                
                // Discard existing value
                var url = $link.val();
                $link.val('');
                
                module._trigger('discard', { url: url });
                return false;
            },
            
            _discardUpload: function () 
            {
                var module = this, $el = this.el;
                
                var $file = $el.find('.controls.choose-method input[type=file]');

                $el.children('.controls.upload-file').hide();
                $el.children('.controls.choose-method').show();
                
                // Discard the URL generated as a result of a previous upload (if any)
                var url = $file.data('url');
                $file.data('url', null);

                // Deselect file (if any)
                $file.val(null);
                
                // Trigger "discard" only if a valid link was there
                if (url) { 
                    module._trigger('discard', { url: url });
                }

                return false;
            },

            _trigger: function (eventType, data)
            {
                 var module = this, opts = this.options; 
                 
                 var message = { 
                    name: module.options.name 
                 };
                 
                 switch (eventType) {
                    case 'ready':
                    case 'discard':
                        $.extend(message, { url: data.url });
                        break;
                    default:
                        assert(false); /* unreachable */ 
                 }
                 
                 //debug('About to trigger "' + eventType + '" with message:', message);
                 module.el.trigger(opts.eventPrefix + eventType, [message]);
                 
                 return;
            },
            
            _proceedWithLink: function (ev) 
            {
                var module = this;
                
                var $link = module.el.find('.controls.link-file input[type=url]');
                module._trigger('ready', { url: $link.val() });

                return false;
            },
            
            _proceedWithUpload: function (ev) 
            {
                var module = this, $el = this.el;

                var $btn = $(ev.target);
                var $form = $el.closest('form');

                var $file = $el.find('input:file');
                var fileobj = $file.prop('files').item(0);
                
                var form_data = $form.serializeArray(); 
                form_data.push({ name: 'name', value: module.options.name });
                
                // Start upload

                var ajax_opts = {
                    type: 'post',
                    // Provide options specific to iframe transport.
                    // Note: Using ajax transport (dependency of jquery-fileupload) from 
                    // https://github.com/blueimp/jQuery-File-Upload
                    dataType: 'iframe json', 
                    fileInput: $file,
                    formData: form_data,
                };
                
                $.ajax($form.prop('action'), ajax_opts) 
                    .done(function (data, statusText, jqxhr) { 
                        debug('Finished uploading:', fileobj.name)
                        // We assume server's response contains a key "url" under
                        // which it reports the URL generated for the upload
                        assert($.isPlainObject(data));
                        assert(data.url && data.size && data.size == fileobj.size);
                        $file.data('url', data.url);
                        module._trigger('ready', data);
                    })
                    .fail(function (jqxhr, statusText) {
                        warn('Failed to upload:', fileobj.name)
                        $file.data('url', null);
                    })
                    .always(function () {
                        module._refreshLoadingButton($btn, false);
                    });
               
                module._refreshLoadingButton($btn, true);
                
                debug('Started upload:', fileobj.name)
                return false;
            },
        };
    });

}).apply(this);
