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
});

