(function ($) {
    $(document).ready(function () {
        $(".raster-export-button").on("click", function(){
            var request = 'http://labs.geodata.gov.gr/rasdaman/ows/?service=WCS&version=2.0.1&request=ProcessCoverages&query=for c in (coverage_id) return encode(c, "format")'
            var $this = $(this);
            var coverage_id =$this.attr("data-resource-id");
            var coverage_format =$this.attr("data-resource-format");
            var filledRequest = request.replace('coverage_id', coverage_id).replace('format', coverage_format);
            window.open(filledRequest, "_blank")
        })
    })
})(jQuery);