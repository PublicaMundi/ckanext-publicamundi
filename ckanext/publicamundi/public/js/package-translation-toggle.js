ckan.module('package-translation-toggle', function (jQuery, _) {
    return {
        options:{
            i18n:{
                translate_button: _('Edit'),
                save: _('Save'),
                cancel: _('Cancel'),
            }
        },
        initialize: function () {
            jQuery.proxyAll(this, /_on/);
            this.el.on('change', this._onToggle);
            this.sandbox.subscribe('package-translation-field-changed', this._onToggle);
        },
        _onToggle: function() {
            this.toggle = jQuery(this.el).prop('checked');

            var table = jQuery('.metadata-translation-table:first');
            if (this.toggle === true){
                table.find('.text').each(function (idx, field){
                    jQuery(this).text(jQuery(this).attr('data-module-translated-text'));
                });
            }
            else if(this.toggle === false){
                table.find('.text').each(function (idx, field){
                    jQuery(this).text(jQuery(this).attr('data-module-source-text'));
                });

            }

        }
  };
});
