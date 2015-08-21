ckan.module('contact-form-send', function ($, _) {
      return {
          options: {
            },
            elements: {
            },
            initialize: function () {
                $.proxyAll(this, /_on/);
                this._generateCaptcha();
                this.el.on('submit', this._onSubmit); 
                //this.el.on('hidden.bs.modal', this._onHidden);
                //$("#contact-form-modal-send").on('click', this._onSubmit);
                $("#contact-form-modal-reload").on('click', this._onReload);
            },
            _generateCaptcha: function() {
                var url = '/publicamundi/util/generate_captcha';
                $.ajax({
                    url: url,
                    type: 'POST',
                    data: {},
                    success: function(data){
                        $("#contact-form-modal #contact-captcha-img").attr("src", data);  
                    },
                })

            },
            _onReload: function(e) {
                e.preventDefault();
                this.el[0].reset();
                this._generateCaptcha();
                $('#contact-form-modal-loading').addClass('hidden');
                $('#contact-form-modal-failure').addClass('hidden');
                $('#contact-form-modal-success').addClass('hidden');
                $('#contact-form-modal-ok').addClass('hidden');
                $('#contact-form-modal-items').removeClass('hidden');
                $('#contact-form-modal-send').removeClass('hidden');
                $('#contact-form-modal-clear').removeClass('hidden');
                $('#contact-form-modal-cancel').removeClass('hidden');
                $('#contact-form-modal-wrong-captcha').addClass('hidden');

            },
            _onSubmit: function(e){
                e.preventDefault();
                var url = '/publicamundi/util/send_email';
                var data = {
                    'name': $("#contact-form-modal #contact-name").val(),
                    'email': $("#contact-form-modal #contact-email").val(), 
                    'pkg_name': $("#contact-form-modal #contact-pkg_name").val(), 
                    'message': $("#contact-form-modal #contact-msg").val(), 
                    'antispam': $("#contact-form-modal #contact-antispam").val(), 
                    'captcha': $("#contact-form-modal #contact-captcha-txt").val(), 
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
                $('#contact-form-modal-wrong-captcha').addClass('hidden');
                $('#contact-form-modal-loading').removeClass('hidden');
                $('#contact-form-modal-cancel').addClass('hidden');
            },
            _onSuccess: function(data) {
                //console.log(data);
                var response = JSON.parse(data);
                //console.log(response.success);
                
                // Mail sent
                if (response.success){
                    $('#contact-form-modal-loading').addClass('hidden');
                    $('#contact-form-modal-success').removeClass('hidden');
                    $('#contact-form-modal-send').addClass('hidden');
                    $('#contact-form-modal-ok').removeClass('hidden');
                    $('#contact-form-modal-cancel').addClass('hidden');

                }
                else{
                    // Mail not sent - wrong captcha entered
                    if (response.error == 'wrong-captcha'){
                        $('#contact-form-modal-loading').addClass('hidden');
                        $('#contact-form-modal-items').removeClass('hidden');
                        $('#contact-form-modal-wrong-captcha').removeClass('hidden');
                        $('#contact-form-modal-cancel').removeClass('hidden');
                        this._generateCaptcha();

                    }
                }                
            },
            _onFailure: function(data){
                console.log(data);
                $('#contact-form-modal-loading').addClass('hidden');
                $('#contact-form-modal-items').addClass('hidden');
                $('#contact-form-modal-send').addClass('hidden');
                $('#contact-form-modal-failure').removeClass('hidden');
                $('#contact-form-modal-clear').addClass('hidden');
                $('#contact-form-modal-ok').removeClass('hidden');
                $('#contact-form-modal-cancel').addClass('hidden');
                                
            },

                          
      };
});
