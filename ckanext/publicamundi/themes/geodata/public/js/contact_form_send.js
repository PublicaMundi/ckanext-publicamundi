ckan.module('contact-form-send', function ($, _) {
      return {
          options: {
            },
            elements: {
            },
            initialize: function () {
                $.proxyAll(this, /_on/);
                this.el.on('submit', this._onSubmit); 
                this.el.on('hidden.bs.modal', this._onHidden);
            },
            _onHidden: function(e) {
                this.el[0].reset();
                // do i want this? 
                //$('#contact-form-modal-loading').addClass('hidden');
                //$('#contact-form-modal-success').addClass('hidden');
                //$('#contact-form-modal-items').removeClass('hidden');

            },
            _onSubmit: function(e){
                e.preventDefault();
                var url = '/epikoinwnia';
                var data = {
                    'name': $("#contact-form-modal #contact-name").val(),
                    'email': $("#contact-form-modal #contact-email").val(), 
                    //'subject': $("#contact-form-modal #contact-subject").val(), 
                    'pkg_name': $("#contact-form-modal #contact-pkg_name").val(), 
                    'message': $("#contact-form-modal #contact-msg").val(), 
                    'antispam': $("#contact-form-modal #contact-antispam").val(), 
                };
                $.ajax({
                    url: url,
                    type: 'POST',
                    data: data,
                    success: this._onSuccess,
                    failure: this._onFailure,
                    error: this._onFailure,
                    beforeSend: this._beforeSend,
                })
                
            },
            _beforeSend: function(data) {
                $('#contact-form-modal-items').addClass('hidden');
                $('#contact-form-modal-loading').removeClass('hidden');
            },
            _onSuccess: function(data) {
                //alert("Mail sent succesfully");
                $('#contact-form-modal-loading').addClass('hidden');
                $('#contact-form-modal-items').addClass('hidden');
                $('#contact-form-modal-success').removeClass('hidden');
                $('#contact-form-modal-send').addClass('hidden');
                $('#contact-form-modal-ok').removeClass('hidden');
            },
            _onFailure: function(data){
                //alert("Mail hasn't been sent");
                console.log(data);
                $('#contact-form-modal-loading').addClass('hidden');
                $('#contact-form-modal-items').addClass('hidden');
                $('#contact-form-modal-send').addClass('hidden');
                $('#contact-form-modal-failure').removeClass('hidden');
                $('#contact-form-modal-send').addClass('hidden');
                $('#contact-form-modal-ok').removeClass('hidden');

            },

                          
      };
});
