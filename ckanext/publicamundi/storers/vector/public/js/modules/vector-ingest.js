var layers_array;

function simple_layer(idx) {
    this.idx = idx;
    this.name = $("#layer_name_" + idx).val();
    this.srs = $("#layer_srs_" + idx).val();
    this.encoding = $("#layer_encoding_" + idx).val();
    this.is_selected = $("#checkbox_" + idx).prop("checked");
};

ckan.module('vector-ingest', function(jQuery, _) {
    return {

        options: {
            validation_url: null,
            gdal_driver: null,
            ingest_base_url: null,
            layers: null,
        },
        initialize: function() {
            var module = this;
            var validation_url = this.options.validation_url;
            var layersFromOptions = this.options.layers;
            var rules = {};
            var messages = {};

            for (var i = 0; i < layersFromOptions.length; i++) {
                var layer = layersFromOptions[i];
                var layerIdx = layer.idx;
                var layerNameInputName = "layer_name_input";
                var layerSrsInputName = "projection";
                var layerEncodingInputName = "encoding";

                rules[layerNameInputName] = {
                    required: true
                };
                messages[layerNameInputName] = {
                    required: "Layer name is required"
                };

                rules[layerSrsInputName] = {
                    required: true,
                    remote: {
                        id: layerIdx,
                        url: validation_url,
                        type: "get",
                        async: false
                    }
                };
                messages[layerSrsInputName] = {
                    required: "Projection is required",
                    remote: "Not a valid Projection"
                };

                rules[layerEncodingInputName] = {
                    required: true,
                    remote: {
                        id: layerIdx,
                        url: validation_url,
                        type: "get",
                        async: false
                    }
                };
                messages[layerEncodingInputName] = {
                    required: "Layer Encoding is required",
                    remote: "Not a valid Encoding"
                };
            }
            $("#ingest-form").validate({
                onkeyup: false,
                blur: false,
                click: false,
                onfocusout: false,
                onsubmit: true,
                errorPlacement: function(error, element) {
                    $(element).prop('title', error.text());
                },
                rules: rules,
                messages: messages,
                highlight: function(element, errorClass) {

                    $(element).css('border', '1px solid red');
                },
                unhighlight: function(element, errorClass) {
                    $(element).css('border', '1px solid #CCC');
                },

                showErrors: function(errorMap, errorList) {
                    this.defaultShowErrors();
                },
                success: function(element) {

                },

            });
            $('#ingest-form input[type=checkbox]').each(function() {
                $(this).click(function() {
                    var parent = $(this).attr("parent");
                    if (!$(this).prop("checked")) {

                        $(parent).children().find("input[type=text]").each(function() {
                            $(this).prop('disabled', true);
                        });
                    } else {
                        $(parent).children().find("input[type=text]").each(function() {
                            $(this).prop('disabled', false);
                        });
                    }
                });
            });

            $("#ingest-form").on('submit', function(e) {
                e.preventDefault();
                return false;
            });

            $('#ingest_button').click(function(ev) {
                var valid = true;
                $("#ingest-form").valid();
                $("#ingest-form input[type=text]").each(function() {
                    var layer_id = $(this).attr("layer_id");
                    var checkbox = $("#checkbox_" + layer_id);
                    if (checkbox.is(":checked")) {

                        if (!$(this).valid()) {

                            valid = false;
                        } else {
                            $(this).css('border', '1px solid #CCC');
                        }
                    } else {
                        $(this).css('border', '1px solid #CCC');
                    }
                });

                if (valid == true) {

                    module._ingest();
                }
            });
        },
        _ingest: function() {
            // Start the ingestion

            layers_array = [];
            var gdal_driver = this.options.gdal_driver;
            var layers = this.options.layers;
            for (var i = 0; i < layers.length; i++) {
                var curr_layer = layers[i];
                layers_array.push(new simple_layer(curr_layer.idx));

            }

            var base_url = (this.options.ingest_base_url);

            var json_data = {
                "layers": layers_array
            };
            $.ajax({
                type: "POST",
                url: base_url,
                dataType: 'json',
                async: false,
                data: {
                    "data": JSON.stringify(json_data)
                },
                success: function() {}
            })
            location.reload();

        },
    };

});