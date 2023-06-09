;(function($) {
    $(document).ready(function() {
      $('input[name="to_assign"]').on('click', function() {
        var selectedCount = $('input[name="to_assign"]:checked').length;
        $('span[name="selected_count"]').text(selectedCount);
      });
    });
  })(jQuery);