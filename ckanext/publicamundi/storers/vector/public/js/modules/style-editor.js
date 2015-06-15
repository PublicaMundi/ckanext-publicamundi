ckan.module('style-editor', function(jQuery, _) {
    return {

        options: {
            edit_current_url: null,
            upload_sld_url: null,
        },
        initialize: function() {
            var module = this;
            $("#edit-current-style").click(function() {
                module._edit_current_style();
            });
            module._edit_current_style();

        },
        teardown: function () {
            // We must always unsubscribe on teardown to prevent memory leaks.
            alert("now");
        },
        _edit_current_style: function() {
            var module = this;
            $("#edit-current-style-tab").addClass("active");
            $("#upload-sld-file-tab").removeClass("active");
            $("#style-content").load(module.options.edit_current_url);
            
        },
        _upload_sld_file: function() {
            var module = this;
            $("#upload-sld-file-tab").addClass("active");
            $("#edit-current-style-tab").removeClass("active");
            $("#style-content").load(module.options.upload_sld_url);
            
        }
    };

});