var module;
this.ckan.module('export-dialog', function (jQuery, _) {
  return {

    /* holds the loaded lightbox */
    modal: null,

    options: {
      template: null
    },

    
    initialize: function () {
      console.log(this.options.template);
      jQuery.proxyAll(this, /_on/);

      this.el.on('click', this._onClick);
      this.el.button();
      
    },

 
    loading: function (loading) {
      this.el.button(loading !== false ? 'loading' : 'reset');
    },

 
    show: function () {
     var sandbox = this.sandbox;
          module = this;

      if (this.modal) {
        return this.modal.modal('show');
      }

      this.loadTemplate().done(function (html) {
        module.modal = jQuery(html);
        module.modal.find('.modal-header :header').append('<button class="close" data-dismiss="modal">×</button>');
        module.modal.modal().appendTo(sandbox.body);
      });
    },

 
    hide: function () {
      if (this.modal) {
        this.modal.modal('hide');
      }
    },

 
    loadTemplate: function () {
      if (!this.options.template) {
        this.sandbox.notify(this.i18n('noTemplate'));
        return jQuery.Deferred().reject().promise();
      }

      if (!this.promise) {
        this.loading();

        // This should use sandbox.client!
        this.promise = jQuery.get(this.options.template);
        this.promise.then(this._onTemplateSuccess, this._onTemplateError);
      }
      return this.promise;
    },

    /* Event handler for clicking on the element */
    _onClick: function (event) {
      event.preventDefault();
      this.show();
    },

    /* Success handler for when the template is loaded */
    _onTemplateSuccess: function () {
      this.loading(false);
    },

    /* error handler when the template fails to load */
    _onTemplateError: function () {
      this.loading(false);
      this.sandbox.notify(this.i18n('loadError'));
    }    
  };
});
