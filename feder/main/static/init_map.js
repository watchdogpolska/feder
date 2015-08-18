(function($) {
    $("#pl_map path").on("click", function() {
        document.location.pathname = $(this).data("href")
    });
})(jQuery);