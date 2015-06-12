ckan.module('download_options_dialog', function ($, _) {
      return {
          options: {
                BASE_URL: 'http://labs.geodata.gov.gr/',
                type: null,
                format: null,
                srs: null,
            },
            elements: {
                active_modal: null,
                format_type: null,
                srs_type: null,
                download_btn: null,
            },
            initialize: function () {
                $.proxyAll(this, /_on/);
                this.el.on('click', this._onClick);
                
            },
            _onClick: function(){
                
                this.elements.active_modal = $('#download_options-'+this.options.id);
                this.elements.format_type = this.elements.active_modal.find('[name="format_type"]');
                this.elements.srs_type = this.elements.active_modal.find('[name="srs_type"]');
                this.elements.download_btn = this.elements.active_modal.find('[name="download"]');
                
                console.log('elements=');
                console.log(this.elements.format_type);
                console.log(this.elements.srs_type);
                console.log(this.elements.download_btn);
                
                var selected = this.elements.format_type.find('option:selected');
                this.options.format = selected.val();
                this.options.srs = this.elements.srs_type.val();
                this.options.type = selected.data('resource-type');
                
                console.log('options=');
                console.log(this.options.format);
                console.log(this.options.srs);
                console.log(this.options.type);

                this.elements.format_type.on('change', this._onTypeSelect);
                this.elements.srs_type.on('change', this._onSrsSelect);
               
                this.elements.download_btn.on('click', this._onDownloadClicked);
                this._onUpdateDownloadButton();

            },
            _onTypeSelect: function(e) {
                var selected = this.elements.format_type.find('option:selected');
                this.options.format = this.elements.format_type.val();
                this.options.type = selected.data('resource-type');
                console.log('options=');
                console.log(this.options.format);
                console.log(this.options.srs);
                console.log(this.options.type);

                this._onUpdateDownloadButton();

            },
            _onSrsSelect: function(e){
                this.options.srs = this.elements.srs_type.val();
                this._onUpdateDownloadButton();

                console.log('options=');
                console.log(this.options.format);
                console.log(this.options.srs);
                console.log(this.options.type);


            },
            _onUpdateDownloadButton: function(){
                if (this.options.type == "vector"){
                    this.elements.download_btn.attr("href", this._onGetVectorUrl());
                    $('.control-srs_type').removeClass('hide');
                    //this.elements.download_btn.removeClass('hide');
                }
                else if (this.options.type == "raster"){
                    this.elements.download_btn.attr("href", this._onGetRasterUrl());
                    $('.control-srs_type').addClass('hide');
                    //this.elements.download_btn.removeClass('hide');
                }
                else{
                    //this.elements.download_btn.addClass('hide');
                    this.elements.download_btn.attr("href", '#');
                    //this.elements.download_btn.attr("href", this._onGetVectorUrl());
                    $('.control-srs_type').addClass('hide');
                }
            },
            _onDownloadClicked: function(e){
                
                // hide modal
                this.elements.active_modal.modal('hide');
                //e.preventDefault();
                //alert('download clicked');
            },
            _onGetRasterUrl: function(){
                var service = 'WCS';
                var version = '2.0.1';
                var request = 'ProcessCoverages';
                
                var selected = this.elements.format_type.find('option:selected');
                var coverage_id = selected.data('resource-id');
                var format = selected.data('resource-format');
                
                var query = 'for c in ('+coverage_id+') return encode(c, "'+format+'")';

                var url = this.options.BASE_URL+'rasdaman/ows/?service='+service+'&version='+version+'&request='+request+'&query='+query;
                console.log(url); 
                return url;

                //var request = 'http://labs.geodata.gov.gr/rasdaman/ows/?service=WCS&version=2.0.1&request=ProcessCoverages&query=for c in (coverage_id) return encode(c, "format")'

            },
            _onGetVectorUrl: function(){
                var service = 'WFS';
                var version = '1.0.0';
                var request = 'GetFeature';
                
                var selected = this.elements.format_type.find('option:selected');
                console.log(selected);
                var layer_name = selected.data('resource-layer');
                var format = selected.data('resource-format');
                var srs = this.options.srs;
                
                var url = this.options.BASE_URL+'geoserver/wfs/?service='+service+'&version='+version+'&request='+request+'&typeName='+layer_name+'&outputFormat='+format+'&srs='+srs;
              /*  qs_params = OrderedDict([
                    ('service', 'WFS'),
                    ('version', '1.0.0'),
                    ('request', 'GetFeature'),
                    ('typeName', str(layer_name)),
                    ('outputFormat', str(output_format)),
                    ('srs', str(srs)),
                ])
                return service_endpoint + '?' + urllib.urlencode(qs_params) */

                return url;
            },
              
      };
});
