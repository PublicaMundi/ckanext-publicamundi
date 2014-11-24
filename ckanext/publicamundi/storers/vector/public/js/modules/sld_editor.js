
this.ckan.module('sld_editor', function (jQuery, _) {

 
    
  
  return {
    options: {
      i18n: {
      }
    },

    initialize: function () {
      jQuery.proxyAll(this, /_on/);
      this.el.ready(this._onReady);
    },

    _onReady: function() {

      
      var editor = CodeMirror.fromTextArea(document.getElementById("sld_body"), {
        mode: "xml",
        lineNumbers: true
      });
     
      
    }
  };
});

 

 