(function($) {
    $("#pl_map path").on("click", function() {
        document.location.pathname = $(this).data("href")
    });
    $('[data-toggle="tooltip"]').tooltip({'container': 'body'});
})(jQuery);