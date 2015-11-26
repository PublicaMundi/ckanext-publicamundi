ckan.module('package-translation-change-lang', function (jQuery, _) {
    return {
        options: {
            packageShowUrl: '/api/action/package_show',
        },
        initialize: function () {
            jQuery.proxyAll(this, /_on/);
            
            //publish initial language
            this.sandbox.publish('package-translation-lang-changed', this.el.val());
            //listen for change
            this.options.package = jQuery('#field-package-name').val();
            this.el.on('change', this._onSelect);
        },
        _onSelect: function(e) {
            e.preventDefault();
            var lang = this.el.val();
            this.sandbox.publish('package-translation-lang-changed', lang);
            this.updateTranslationValues(lang);
        },
        updateTranslationValues: function(lang) {
            var url = '/' + lang + this.options.packageShowUrl;
            jQuery.ajax({
                type: "GET",
                url: url,
                data: { 
                    id: this.options.package, 
                }, 
                dataType: 'json',
                async: true,
                //beforeSend: ld,
                //complete: cb,
                success: function(response) {
                    console.log('succeeded');
                    console.log(response);
                    var package = response.result;
                    
                    var table = jQuery('.metadata-translation-table:first');
                    table.find('.text').each(function (idx, field){
                        var qnameArray = jQuery(this).attr('data-module-qname').split(".");
                        //var qnameArray = 'inspire.contact.0.organization'.split(".");
                        var fld=package;
                        for (var idx in qnameArray){
                            var qname = qnameArray[idx];
                            fld=fld[qname];
                        };
                        //console.log(fld);
                        jQuery(this).attr('data-module-translated-text', fld);

                    });

                },
                failure: function(response) {
                    console.log('failed');
                    console.log(response);
                },
                error: function(response) {
                    console.log('error');
                    console.log(response);
                    alert('Error: .\n' + response.status + ':' + response.responseText);
                }
            });
   
        },

  };
});
