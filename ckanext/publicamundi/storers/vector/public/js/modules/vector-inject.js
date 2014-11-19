var layers_array;
function simple_layer(idx){
      this.idx=idx;
      this.srs=$("#layer_srs_"+idx).val();
      this.is_selected= $("#checkbox_"+idx).is(":checked");
};
function tabular_layer(idx){
      this.idx=idx;
      this.srs=$("#layer_srs_"+idx).val();
      this.is_selected= $("#checkbox_"+idx).is(":checked");
};

ckan.module('vector-inject', function (jQuery, _) {
  return {

    options: {
      inject_base_url:null,
      gdal_driver:null,
      layers:null,
    },
    initialize: function () {
    var module = this;    
    
    $("#inject_button").click(function () {
	    module._inject2();
	});


    },
    _inject: function(){
      
      var base_url=(this.options.inject_base_url);
      var inject_url =base_url;
      var gdal_driver= this.options.gdal_driver;
      if (gdal_driver=='ESRI Shapefile'){
	  inject_url=inject_url+ "?projection=" + $('#projection').val() + "&encoding=" +  $('#shp_encoding').val();
	
      }
      else{
	  var selected_layers=[];
	  $('input:checkbox[name=checkbox_layer]:checked').each(function() 
	      {
		selected_layers.push(this.value);
	      });
	  inject_url=inject_url+ "?selected_layers=" +selected_layers ;
	  console.log(inject_url);
      }
      
      
        module.hide();
        window.location = inject_url;
      
    },
    _inject2: function(){
	
	layers_array=[];
	var gdal_driver = this.options.gdal_driver;
	var layers=this.options.layers;
	for (var i = 0; i < layers.length; i++) { 
	    var curr_layer=layers[i];
	    if (false){
	      alert();
	    }
	    else{
		
		layers_array.push(new simple_layer(curr_layer.idx));
	    }
	      
	    }
	
	var base_url=(this.options.inject_base_url);
	 
	var json_data={"layers":layers_array
		      };
	$.ajax
	    ({
		type: "POST",
		url: base_url,
		dataType: 'json',
		async: false,
		data: {"data":JSON.stringify(json_data)},
		success: function () {

		
		}
	    })
	location.reload(); 
      
    }
  };

});
