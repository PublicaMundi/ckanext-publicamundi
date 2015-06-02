var layers_array;

function simple_layer(idx) {
    this.idx = idx;
    this.name = $("#layer_name_" + idx).val();
    this.srs = $("#layer_srs_" + idx).val();
    this.encoding = $("#layer_encoding_" + idx).val();
    this.is_selected = $("#checkbox_" + idx).is(":checked");
};

function tabular_layer(idx) {
    this.idx = idx;
    this.srs = $("#layer_srs_" + idx).val();
    this.is_selected = $("#checkbox_" + idx).is(":checked");
};

ckan.module('vector-ingest', function(jQuery, _) {
    return {

        options: {
            ingest_base_url: null,
            gdal_driver: null,
            layers: null,
        },
        initialize: function() {
            var module = this;

            $("#ingest_button").click(function() {
                module._ingest();
            });


        },
        _ingest: function() {

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
                success: function() {


                }
            })
            location.reload();

        }
    };

});