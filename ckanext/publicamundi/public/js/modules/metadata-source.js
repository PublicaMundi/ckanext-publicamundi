(function () {

    var debug = $.proxy(window.console, 'debug')
    var warn = $.proxy(window.console, 'warn')
    
    this.ckan.module('import-metadata-dialog', function ($, _) {

        return {
            
            config: {
                dialog: {
                    container: '#content .wrapper', 
                    id: 'import-metadata-dialog',
                    template: 'import-metadata-dialog.html',
                    createOptions: {
                        show: false, 
                        keyboard: false, 
                        backdrop: 'static',
                    },
                },
            },
            
            options: {
                targetUrl: null,
            },
            
            initialize: function () 
            {
                var module = this,
                    opts = this.options,
                    config = this.config,
                    sandbox = this.sandbox;
                
                module.$container = $(config.dialog.container);
                module.$form = module.el.closest('form')
                
                sandbox.client.getTemplate(config.dialog.template, {
                        id: config.dialog.id 
                    }, function (markup) {
                        var $dialog = null;
                        // Create dialog
                        $dialog = $(markup)
                            .modal(config.dialog.createOptions)
                            .appendTo(module.$container)
                            .on('shown', $.proxy(module._prepareDialog, module))
                    }
                );
                
                module.el.find('.open-dialog')
                    .on('click', function () {
                        var $dialog = module.$container.find('#' + config.dialog.id)
                        $dialog.modal('show');
                        return false;
                    })

                debug('Initialized module: import-metadata-dialog opts=', opts)
            },

            teardown: function () 
            { 
                debug('Tearing down module: import-metadata-dialog')
            },

            _initializeDialog: function ()
            {
                var module = this, config = this.config;

                var $dialog = module.$container.find('#' + config.dialog.id);
                
                $dialog.find('[data-module]').each(function (i, el) {
                    setTimeout(function () {
                        ckan.module.initializeElement(el);
                    }, 0);
                }); 
                
                $dialog.find('.cancel')
                    .on('click', $.proxy(module._handleCancel, module))
            
                return;
            },

            _prepareDialog: function ()
            {
                var module = this, 
                    config = this.config, opts = this.options;
                
                debug('Prepare import-metadata-dialog dialog');
                
                var $dialog = module.$container.find('#' + config.dialog.id);
                
                if (!$dialog.data('initialized')) {
                    module._initializeDialog();
                    $dialog.data('initialized', true);
                }
                
                var $dtype = module.$form.find('select[name="dataset_type"]')
                var dtype = $dtype.val();

                $dialog.find('.modal-header h3 > .name')
                    .text($dtype.find('option[value="' + dtype + '"]').text())
                
                $dialog.find('.finish')
                    .attr('disabled', 'disabled');
                
                // Todo Reset upload-link widget

                $dialog.find('div.import-step form')
                    .on('upload-link:ready', function (ev, message) {
                        var p = { source: message.url, type: dtype };
                        $.get(opts.targetUrl, p, 'json')
                            .always(function () {
                                $dialog.find('div.import-step').fadeOut(400, function () {
                                    $dialog.find('div.results-step').show();
                                });
                            })
                            .done(function (data) {
                                debug('Imported metadata from ' + message.url);
                                $('<p>').addClass('message info')
                                    .text('Imported metadata: ' + data.success)
                                    .appendTo($dialog.find('div.results-step'))
                                $dialog.find('a.finish').attr('disabled', null)
                            })
                            .fail(function () {
                                warn('Failed to import metadata from ' + message.url);
                                $('<p>').addClass('message error')
                                    .text('Failed to import metadata')
                                    .appendTo($dialog.find('div.results-step'))
                            })
                        return false;
                    })
                    .on('upload-link:discard', function (ev, message) {
                        return false;
                    });

                $dialog.find('div.import-step').show();

                $dialog.find('div.results-step').hide();
                
                return true;
            },           
            
            _handleCancel: function ()
            {
                var module = this, config = this.config;

                var $dialog = module.$container.find('#' + config.dialog.id);

                debug('Cleanup import-metadata-dialog dialog (cancelled)');
                
                $dialog.find('div.import-step form')
                    .off('upload-link:ready')
                    .off('upload-link:discard');
                
                $dialog.find('div.results-step').empty();

                $dialog.modal('hide');
                
                return true;
            },

        };
    });

}).apply(this);
