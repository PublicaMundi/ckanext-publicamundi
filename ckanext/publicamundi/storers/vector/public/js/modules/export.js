ckan.module('export-module', function(jQuery, _) {
    return {

        options: {
            base_url: '',
            non_srs_formats: [
                "kml",
                "csv",
                "xls",
                "xlsx",
                "gpx",
                "pdf"
            ],
        },
        initialize: function() {
            var module = this;
            $('#field-export_format').on('change', function() {
                module._export_format_changed(this.value)
            });

            $('#export_button').on("click", function() {
                module._init_export()
            });
        },
        _export_format_changed: function(new_value) {
            found = (this.options.non_srs_formats.indexOf(new_value) > -1);
            $('#gml_format_select').hide();
            $('#div_tabular').hide();
            if (found) {
                this._clear_previous_errors();
                $('#divproj').hide();
            } else {
                if ($('#divproj').is(":hidden")) {

                    $('#divproj').show();
                }
            }
            if (new_value == 'csv' || new_value == 'xls') {

                $('#div_tabular').show();
            } else if (new_value == 'gml') {
                $('#gml_format_select').show();

            }

            $('#check_geom_export').click(function() {
                if ($('#check_geom_export').prop('checked')) {
                    $('#csv_formats').children().prop('disabled', false);
                } else {
                    $('#csv_formats').children().prop('disabled', true);
                }

            });

        },
       _init_export: function() {

            projection = $('#layer_srs_0').val();
            export_format = $('#field-export_format').val();
            if (this.options.non_srs_formats.indexOf(export_format) < 0) {
                if (this._is_valid_srs(projection)) {
                    this._clear_previous_errors();
                    this._do_request();
                } else {

                    this._raise_bad_srs(projection);
                }
            } else {

                this._do_request();
            }


        },
        _do_request: function() {

            if ($('#divproj').is(":hidden")) {
                proj = 4326;
            } else {
                proj = $('#layer_srs_0').val();
            }
            var export_url = this.options.base_url + "?format=" + $('#field-export_format').val() + "&projection=" + proj;

            if ($('#field-export_format').val() == 'csv') {
                if ($('#check_geom_export').prop('checked')) {
                    var csv_geom = $('input[name=csv_export_geom]:checked').val();
                    export_url += "&csv_geom=" + csv_geom;
                }
            } else if (($('#field-export_format').val() == 'gml')) {
                var gml_version = $('#field-gml-export_format').val();
                export_url += "&gml_version=" + gml_version;
            }
            window.location = export_url;

        },
        _is_valid_srs: function(projection) {
            //         if (epsg_list.indexOf(projection) >= 0) {
            //                     return true;
            //                 } else {
            //                     return false;
            //                 }
            return true;

        },
        _clear_previous_errors: function() {
            $("#proj-error").text('');
        },
        _raise_bad_srs: function(projection) {
            $("#proj-error").show();
            $("#proj-error").text('Projection ' + projection + ' is invalid. Please select a valid one!');
        },
    };

});