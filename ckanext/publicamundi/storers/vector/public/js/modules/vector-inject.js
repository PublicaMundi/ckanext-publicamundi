ckan.module('vector-inject', function (jQuery, _) {
  return {

    options: {
      inject_base_url:null,     
    },
    initialize: function () {
    
    var module = this;    
    
    $("#inject_button").click(function () {
	    module._inject();
	});


    },
    _inject: function(){
      var base_url=(this.options.inject_base_url);
 
      var inject_url=base_url+ "?projection=" + $('#projection').val() + "&encoding=" +  $('#shp_encoding').val();
      
      module.hide();
      window.location = inject_url;
      
    }
  };

});
