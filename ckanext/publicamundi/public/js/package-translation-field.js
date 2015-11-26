ckan.module('package-translation-field', function (jQuery, _) {
    return {
        options:{
            language: 'en',
            updateFieldUrl: '/api/action/package_translation_update_field',
            i18n:{
                translate_button: _('Edit'),
                save: _('Save'),
                cancel: _('Cancel'),
                },
            template: [
                '<div class="modal modal-package-translation">',
                '<div class="modal-header">',
                '<button type="button" class="close" data-dismiss="modal">×</button>',
                '<h3></h3>',
                '</div>',
                '<div class="modal-body">',
                '<textarea class="text-original" rows="8" cols="35" readonly></textarea>',
                '<textarea class="text-translation" rows="8" cols="35"></textarea>',
                '</div>',
                '<div class="modal-footer">',
                '<button class="btn btn-cancel"></button>',
                '<button class="btn btn-primary"></button>',
                '</div>',
                '</div>'
                ].join('\n')
        },
        initialize: function () {
            
            // Grab our button and assign it to a property of our module.
            jQuery.proxyAll(this, /_on/);
            this.status_icon = $('<span/>',
                    {
                        class: 'pull-right icon-pencil'
                    });
                    
            this.options.package = jQuery('#field-package-name').val();
            this.el.parent().append(this.status_icon).end();
            this.el.parent().on('mouseenter', this._onMouseEnter);
            this.el.parent().on('mouseleave', this._onMouseLeave);

            //listen for language change
            this.sandbox.subscribe('package-translation-lang-changed',this._onLangChanged);
        },       
        _onMouseEnter: function(e) {
             this.trans_button = $('<button/>',
             {
                text: this.i18n('translate_button'),
                class: 'btn-mini btn-translation pull-right',
                click: this._onTranslateClick 
             });
             this.el.css('background','#efe8cd');
             this.el.parent().append(this.trans_button).end();
        },
        _onMouseLeave: function(e) {
            if (this.trans_button){
                this.trans_button.remove();
            }
            this.el.css('background','#fff');
        },
        _onLangChanged: function(lang){
            this.language = lang;
        },
        _onTranslateClick: function(e) {
            e.preventDefault();

            this.sandbox.body.append(this.createModal());
            this.modal.modal('show');

            // Center the modal in the middle of the screen.
            this.modal.css({
                'margin-top': this.modal.height() * -0.5,
                'top': '50%'
            });

        },
        createModal: function () {
            if (!this.modal) {
                var element = this.modal = jQuery(this.options.template);
                element.on('click', '.btn-primary', this._onConfirmSuccess);
                element.on('click', '.btn-cancel', this._onDismiss);
                element.modal({show: false});
                element.find('h3').text(this._getFieldTitle());
                element.find('.text-original').text(this.options.sourceText);
                element.find('.text-translation').text(this.options.trans_title);
                element.find('.btn-primary').text(this.i18n('save'));
                element.find('.btn-cancel').text(this.i18n('cancel'));
            }
            //create modal dismiss function
            this.modal.on('hidden.bs.modal', this._onDismiss);
            return this.modal;

        },

        /* Event handler for the success event */
        _onConfirmSuccess: function (event) {
            this.modal.modal('hide');
            var self = this;
            var url = '/' + this.language + this.options.updateFieldUrl;
            var data = {
                    id: this.options.package,
                    key: this.options.qname,
                    value: this.modal.find('.text-translation').val()
                };
            console.log('trying to reach API at');
            console.log(url);
            console.log('with data');
            console.log(data);
            jQuery.ajax({
                type: "POST",
                url: url, 
                data: data,
                dataType: 'json',
                async: true,
                //beforeSend: ld,
                //complete: cb,
                success: function(response) {
                    console.log('succeeded');
                    console.log(response);
                    //save translated term under element attribute
                    self.el.attr('data-module-translated-text', this.modal.find('.text-translation').val());
                    // publish to sandbox to update according to toggle
                    self.sandbox.publish('package-translation-field-changed');
                    self.status_icon.removeClass('icon-pencil').addClass('icon-ok-sign');

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

        /* Event handler for the cancel event */
        _onDismiss: function (event) {
            this.modal.modal('hide');
            
            // publish to sandbox to update according to toggle
            //this.sandbox.publish('package-translation-field-changed');
            this.status_icon.removeClass('icon-ok-sign').addClass('icon-pencil');
        }, 
        _getFieldTitle: function(){
            var titles = this.el.closest('td').parent().find('th');
            var titlesArray = [];
            if (titles.length){
                var head = titles.first();
                var lastChar = parseInt(head.text().substr(head.text().length - 1));
                if (!isNaN(lastChar) && lastChar > 1){
                    head = head.parent();
                    for (var i=0; i<lastChar-1; i++){
                        head = head.prev();
                    }
                    titlesArray.push(head.children().first().text());
                }
            }

            var tmp = jQuery(titles).map(function() {                
                return jQuery(this).text();
              }).get();  
            titlesArray = titlesArray.concat(tmp); 
                 
            var titleDD = this.el.closest('dd').prev();
            if (titleDD.length){
                titlesArray.push(titleDD.text());
            }
            return titlesArray.join(' / ');
        }
        
    
  };
});
