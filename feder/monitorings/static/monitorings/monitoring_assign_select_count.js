document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input[name="to_assign"]').forEach(function (input) {
        input.addEventListener('click', function () {
            var selectedCount = document.querySelectorAll('input[name="to_assign"]:checked').length;
            document.querySelectorAll('span[name="selected_count"]').forEach(function (span) {
                span.textContent = selectedCount;
            });
        });
    });
});
