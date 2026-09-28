/**
 * Adds additional utility buttons to form groups having "checkbox-utils" class
 * which allows user to select unselect all options in CheckboxSelectMultiple widgets.
 */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.checkbox-utils').forEach(function (elem) {
        var legend = elem.querySelector('legend.form-label');
        if (!legend) {
            return;
        }

        var unselectBtn = document.createElement('button');
        unselectBtn.type = 'button';
        unselectBtn.className = 'btn btn-primary unselect-all-btn';
        unselectBtn.textContent = 'Odznacz wszystkie';

        var selectBtn = document.createElement('button');
        selectBtn.type = 'button';
        selectBtn.className = 'btn btn-primary select-all-btn';
        selectBtn.textContent = 'Zaznacz wszystkie';

        legend.after(unselectBtn, selectBtn);

        selectBtn.addEventListener('click', function () {
            elem.querySelectorAll('input[type="checkbox"]').forEach(function (cb) {
                cb.checked = true;
            });
        });
        unselectBtn.addEventListener('click', function () {
            elem.querySelectorAll('input[type="checkbox"]').forEach(function (cb) {
                cb.checked = false;
            });
        });
    });
});
