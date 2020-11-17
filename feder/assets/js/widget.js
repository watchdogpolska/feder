/**
 * Adds additional utility buttons to form groups having "checkbox-utils" class
 * which allows user to select unselect all options in CheckboxSelectMultiple widgets.
 */
$(function () {
    var $inputs = $('.checkbox-utils');

    $inputs.each(function (index) {
        var $elem = $(this),
            $label = $elem.find('label.control-label:first-child');

        $label.after(
            '<button class="btn btn-primary unselect-all-btn" type="button">' +
                'Odznacz wszystkie' +
            '</button>' +
            '<button class="btn btn-primary select-all-btn" type="button">' +
                'Zaznacz wszystkie' +
            '</button>'
        );

        $('.checkbox-utils .select-all-btn').click(function (event) {
            $elem.find('input[type="checkbox"]').prop("checked", true);
        });
        $('.checkbox-utils .unselect-all-btn').click(function (event) {
            $elem.find('input[type="checkbox"]').prop("checked", false);
        });
    });
});
