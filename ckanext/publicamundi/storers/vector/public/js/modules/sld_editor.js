this.ckan.module('sld_editor', function(jQuery, _) {
    return {
        options: {
           post_sld_url: null,
        },
        initialize: function() {
            var module = this;
            jQuery.proxyAll(this, /_on/);
            this.el.ready(this._onReady);
            
            $("#submit_style").click(function() {
                module._submit_style()
            });
        },
        _onReady: function() {
            this.options.editor = CodeMirror.fromTextArea(document.getElementById("sld_body"), {
                mode: "xml",
            });

        },
        _submit_style: function() {
           var sld_body =  this.options.editor.getValue()
           var post_sld_url = this.options.post_sld_url;

           $.ajax({
                type: "POST",
                url: post_sld_url,
                async: false,
                data: {
                    "sld_body": sld_body
                },
                success: function(data) {
                    $("#style-content").html(data);                   
                }
            })

        }
    };
});