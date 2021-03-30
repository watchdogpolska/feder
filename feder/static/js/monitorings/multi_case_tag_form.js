$(function () {
    var OPERATION_ADD = 1,
        OPERATION_REMOVE = 2;

    function submitMultiTagForm (operation) {
        var payload = {
           tags: [],
           cases: [],
           operation: operation
        };

        $('input[name^=select-case-]:checked').each(function (index) {
            payload.cases.push(parseInt($(this).val()));
        });
        $('input[name^=multi-case-tag-]:checked').each(function (index) {
            payload.tags.push(parseInt($(this).val()));
        });

        $.ajax({
            url: monitoringCaseTagsUpdateUrl,
            type: 'post',
            data: JSON.stringify(payload),
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            success: function (data, status, xhr) {
                if (xhr.status == 202) {
                    window.location.reload(true);
                } else {
                    alert('Something went wrong. Status code: ' + xhr.status + '.')
                    console.log(data, status, xhr);
                }
            }
        });
    }

    $('#multi-case-tag-assign-btn').on('click', function (event) {
        event.preventDefault();
        submitMultiTagForm(OPERATION_ADD);
    });

    $('#multi-case-tag-remove-btn').on('click', function (event) {
        event.preventDefault();
        submitMultiTagForm(OPERATION_REMOVE);
    });
});
