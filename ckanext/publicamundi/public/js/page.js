//                                                       //
// Modules needed by every page in ckanext-publicamundi  //
//                                                       //

/*
 * Provide support for select2-based inputs.
 * This module only acts as a (simplified) wrapper to select2
 * functionality.
 */
this.ckan.module('input-select2', function ($, _) {
  return {
    options: {
        width: 'element',
        placeholder: null,
        minimuminputlength: null,
        maximuminputlength: null,
        minimumresultsforsearch: -1,
        tags: null,
        separator: null,
    },
    
    initialize: function() 
    {
        var module = this
        if ($.fn.select2) {
            
            // Prepare init options for a select2 widget
            
            var opts = $.extend({}, {
                placeholder: module.options.placeholder,
                width: module.options.width, 
            })

            if (module.options.minimumresultsforsearch != null) {
                opts.minimumResultsForSearch = Number(module.options.minimumresultsforsearch) 
            } 
            
            if (module.options.tags != null) {
                var t = typeof(module.options.tags) 
                if (t == 'boolean') {
                    opts.tags = module.options.tags
                } else if (t == 'string') {
                    var tags = module.options.tags.split(',')
                    opts.tags = $.map(tags, function(v) { return v.trim() })
                }
            }

            if (module.options.minimuminputlength != null) {
                opts.minimumInputLength = Number(module.options.minimuminputlength)
            }

            if (module.options.maximuminputlength != null) {
                opts.maximumInputLength = Number(module.options.maximuminputlength)
            }
            
            // Initialize select2 widget

            window.console.info('Creating select2 widget with: ' + JSON.stringify(opts))
            
            $(this.el).select2(opts)

        } else {
            window.console.error('The jQuery extension "select2" is not loaded')
        }
        window.console.log('Initialized module: input-select2')
    },
    
    teardown: function() 
    { 
        window.console.log('Tearing down module: input-select2')
    },
  }
})

/*
 * A module for select2-based input for tags
 */
this.ckan.module('input-select2-tags', function ($, _) {
  return {

    options: {
        width: 'element',
        placeholder: null,
        minimuminputlength: 2,
        maximuminputlength: 24,
        tags: null,
        separator: null,
        query: null,
        itemize: false, 
    },
    
    initialize: function() 
    {
        var module = this
        if ($.fn.select2) {
            
            // Prepare init options for a select2 widget
            
            var opts = $.extend({}, {
                placeholder: module.options.placeholder,
                width: module.options.width,
                minimumResultsForSearch: -1,
            })

            if (module.options.tags != null) {
                var t = typeof(module.options.tags) 
                if (t == 'boolean') {
                    opts.tags = module.options.tags
                } else if (t == 'string') {
                    var tags = module.options.tags.split(',')
                    opts.tags = $.map(tags, function(v) { return v.trim() })
                }
            }

            if (module.options.minimuminputlength != null) {
                opts.minimumInputLength = Number(module.options.minimuminputlength)
            }

            if (module.options.maximuminputlength != null) {
                opts.maximumInputLength = Number(module.options.maximuminputlength)
            }
            
            var qname = module.el.attr('name')

            if (module.options.itemize) {
                // Replace original input with a pseudo-input and provide N hidden inputs,
                // where N is the number of entered tags.
                var $h = $('<div>').addClass('hide itemized-tags')
                
                module.el.attr('name', qname + '-' + 'joined')
                $h.appendTo(module.el.closest('.controls'))

                var itemize_tags = function() {
                    var $input = module.el
                    var $h = $input.closest('.controls').find('.itemized-tags')
                    var tags = $input.val().split(',')
                    tags = $.grep(tags, function (tag) { return tag.length })
                    $h.empty()
                    $.each(tags, function (i, tag) {
                        var $i = $('<input>')
                            .attr('type', 'hidden')
                            .attr('name', qname + '.' + i.toString())
                            .val(tag)
                        $h.append($i)
                    })
                }

                itemize_tags()
                module.el.on('change', itemize_tags)
            }

            // Initialize select2 widget

            window.console.info('Creating select2 widget with: ' + JSON.stringify(opts))
            
            $(this.el).select2(opts)

        } else {
            window.console.error('The jQuery extension "select2" is not loaded')
        }
        window.console.log('Initialized module: input-select2-tags')
    },
    
    teardown: function() 
    { 
        window.console.log('Tearing down module: input-select2-tags')
    },
    
    _randName: function(prefix) 
    {
        return prefix + Math.random().toString(36).substring(2)
    },
  }
})

/*
 * (deprecated)
 * A simple module to provide collapsible fieldsets in forms
 */
this.ckan.module('collapsible-fieldset', function ($) {
  return {
    options: {
        state: 'open',
    },
    initialize: function () {
        var $fieldset = this.el
        var $legend   = this.el.find("legend");
        var $body     = this.el.find(".fieldset-body"); 

        if (!($fieldset.is('fieldset'))) {
            console.error ('Encountered an invalid module-target element')
            return
        }
        
        $fieldset.addClass('module-collapsible-fieldset')

        if (this.options.state == 'closed') {
            $body.hide({duration: 0})
            $legend.find('span.toggle-body').toggleClass('state-closed')
        }
        
        $legend.find("span.hints").hide(); 
        $legend
        .on ('click.collapsible-fieldset', function (ev) {
            $body.toggle();
            $legend.find('span.toggle-body').toggleClass('state-closed')
            return false
        })
        .on ('mouseenter.collapsible-fieldset', function (ev) {
            if ($body.is(':hidden')) {
                $legend.find("span.hints").fadeIn();
            }
            return false
        })
        .on ('mouseleave.collapsible-fieldset', function (ev) {
            $legend.find("span.hints").fadeOut();  
            return false
        });
                
        return
    },
  }
})


/* 
 * This is a modified version of resource-upload-field module
 * Creates a new field for an uploaded file and appends file input into
 * the document.
 *
 * Events:
 *
 * Publishes the 'resource:uploaded' event when a file is successfully
 * uploaded. An callbacks receive an object of resource data.
 *
 * See: http://docs.ckan.org/en/latest/filestore.html 
 *
 * options - form: General form overrides for the upload.
 *
 */
this.ckan.module('metadata-source-upload-field', function (jQuery, _, i18n) {
  return {
    /* Default options for the module */
    options: {
        form: {
            method: 'POST',
            file: 'file',
            params: []
        },
        i18n: {
            label: _('Upload a file'),
            errorTitle: _('An Error Occurred'),
            uploadSuccess: _('Resource uploaded'),
            uploadError: _('Unable to upload file'),
            authError: _('Unable to authenticate upload'),
            metadataError: _('Unable to get data for uploaded file')
        },
        name: null,
    },

    /* Initializes the module,  creates new elements and registers event
     * listeners etc. This method is called by ckan.initialize() if there
     * is a corresponding element on the page.
     */
    initialize: function () {
        jQuery.proxyAll(this, /_on/);
        this.upload = this.el.find('span.resource-upload-field');
        this.setupFileUpload();
    },

    /* Sets up the jQuery.fileUpload() plugin with the provided options. */
    setupFileUpload: function () {
        var options = this.options;

        this.upload.find('label').text(this.i18n('label'));
        this.upload.find('input[type=file]').fileupload({
            type: options.form.method,
            paramName: options.form.file,
            forceIframeTransport: true, // Required for XDomain request. 
            replaceFileInput: true,
            autoUpload: false,
            add:  this._onUploadAdd,
            send: this._onUploadSend,
            done: this._onUploadDone,
            fail: this._onUploadFail,
            always: this._onUploadComplete
        });
    },

    /* Displays a loading spinner next to the input while uploading. This
     * can be cancelled by recalling the method passing false as the first
     * argument.
     *
     * show - If false hides the spinner (default: true).
     *
     * Examples
     *
     *   module.loading(); // Show spinner
     *
     *   module.loading(false); // Hide spinner.
     */
    loading: function (show) {
        this.upload.toggleClass('loading', show);
    },

    /* Requests Authentication for the upload from CKAN. Uses the
     * _onAuthSuccess/_onAuthError callbacks.
     *
     * key  - A unique key for the file that is to be uploaded.
     * data - The file data object from the jQuery.fileUpload() plugin.
     *
     * Examples
     *
     *   onFileAdd: function (event, data) {
     *     this.authenticate('my-file', data);
     *   }
     *
     * Returns an jqXHR promise.
     */
    authenticate: function (key, data) {
        data.key = key;

        var request = this.sandbox.client.getStorageAuth(key);
        var onSuccess = jQuery.proxy(this._onAuthSuccess, this, data);
        return request.then(onSuccess, this._onAuthError);
    },

    /* Requests file metadata for the uploaded file and calls the
     * _onMetadataSuccess/_onMetadataError callbacks.
     *
     * key  - A unique key for the file that is to be uploaded.
     * data - The file data object from the jQuery.fileUpload() plugin.
     *
     * Examples
     *
     *   onFileUploaded: function (event, data) {
     *     this.lookupMetadata('my-file', data);
     *   }
     *
     * Returns an jqXHR promise.
     */
    lookupMetadata: function (key, data) {
        var request = this.sandbox.client.getStorageMetadata(key);
        var onSuccess = jQuery.proxy(this._onMetadataSuccess, this, data);
        return request.then(onSuccess, this._onMetadataError);
    },

    /* Displays a global notification for the upload status.
     *
     * message - A message string to display.
     * type    - The type of message eg. error/info/warning
     *
     * Examples
     *
     *   module.notify('Upload failed', 'error');
     */
    notify: function (message, type) {
        var title = this.i18n('errorTitle');
        this.sandbox.notify(title, message, type);
    },

    /* Fixme: 
     * Creates a unique key for the filename provided. This is a url
     * safe string with a timestamp prepended.
     *
     * filename - The filename for the upload.
     *
     * Examples
     *
     *   module.generateKey('my file');
     *   // => '2012-06-05T12:00:00.000Z/my-file'
     *
     * Returns a unique string.
     */
    generateKey: function (filename) {
        var parts = filename.split('.');
        var extension = jQuery.url.slugify(parts.pop());

        // Clean up the filename hopefully leaving the extension intact.
        filename = jQuery.url.slugify(parts.join('.')) + '.' + extension;
        return jQuery.date.toISOString() + '/' + filename;
    },

    /* Callback called when the jQuery file upload plugin receives a file.
     *
     * event - The jQuery event object.
     * data  - An object of file data.
     *
     * Returns nothing.
     */
    _onUploadAdd: function (event, data) {
        if (data.files && data.files.length) {
            var key = this.generateKey(data.files[0].name);
            this.authenticate(key, data);
        }
    },

    /* Callback called when the jQuery file upload plugin fails to upload a file. */
    _onUploadFail: function () {
        this.sandbox.notify(this.i18n('uploadError'));
    },

    /* Callback called when jQuery file upload plugin sends a file */
    _onUploadSend: function () {
        this.loading();
    },

    /* Callback called when jQuery file upload plugin successfully uploads a file */
    _onUploadDone: function (event, data) {
        // Need to check for a result key. A Google upload can return a 404 if
        // the bucket does not exist, this is still treated as a success by the
        // form upload plugin.
        var result = data.result;
        if (result && !(jQuery.isPlainObject(result) && result.error)) {
            this.lookupMetadata(data.key, data);
        } else {
            this._onUploadFail(event, data);
        }
    },

    /* Callback called when jQuery file upload plugin completes a request
     * regardless of it's success/failure.
     */
    _onUploadComplete: function () {
        this.loading(false);
    },

    /* Callback function for a successful Auth request. This cannot be
     * used straight up but requires the data object to be passed in
     * as the first argument.
     *
     * data     - The data object for the current upload.
     * response - The auth response object.
     *
     * Examples
     *
     *   var onSuccess = jQuery.proxy(this._onAuthSuccess, this, data);
     *   sandbox.client.getStorageAuth(key).done(onSuccess);
     *
     * Returns nothing.
     */
    _onAuthSuccess: function (data, response) {
        data.url = response.action;
        data.formData = this.options.form.params.concat(response.fields);
        data.submit();
    },

    /* Called when the request for auth credentials fails. */
    _onAuthError: function (event, data) {
        this.sandbox.notify(this.i18n('authError'));
        this._onUploadComplete();
    },

    /* Called when the request for file metadata succeeds */
    _onMetadataSuccess: function (data, response) {
        var resource = this.sandbox.client.convertStorageMetadataToResource(response);
        this.sandbox.notify(this.i18n('uploadSuccess'), '', 'success');
        this.sandbox.publish('resource:uploaded', { 
            resource: resource,
            name: this.options.name,
        });
    },

    /* Called when the request for file metadata fails */
    _onMetadataError: function () {
        this.sandbox.notify(this.i18n('metadataError'));
        this._onUploadComplete();
    }
  };
});

/* 
 * This module subscribes an element for a resource:uploaded event 
 * which is (expected to be) fired by a metadata-source-upload module.
 */
this.ckan.module('metadata-source-upload-subscriber', function ($) {
  return {
    options: {
        name: null,
    },
    initialize: function () {
        var el  = this.el
        var mod_options = this.options
        this.sandbox.subscribe('resource:uploaded', function (message) {
            // Check if the publisher sent something we are interested into
            if (message.name == null) {
                /* nop: not interested in unnamed resources */
            } else if ((mod_options.name == null) || (message.name == mod_options.name)) {
                /* yes, we are interested in this: update our input value */
                el.val(message.resource.url)
            }
            return
        })
    },
  }
})


