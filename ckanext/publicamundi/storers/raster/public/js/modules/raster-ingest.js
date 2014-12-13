(function ($) {
    $(document).ready(function () {
        $("#ingest_button").on("click", function () {
            var $this = $(this)
            var resource_id = $this.attr("data-resource-id")
            $.get("/api/raster/publish/" + resource_id, function () {
                $("#resource-message-container").html($this.attr('data-success-message'))
                setTimeout(function () {
                    window.location.reload();
                }, 5000)
            })
        });
    })
})(jQuery);