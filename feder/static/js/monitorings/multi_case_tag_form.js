document.addEventListener('DOMContentLoaded', function () {
    var OPERATION_ADD = 1,
        OPERATION_REMOVE = 2;

    function submitMultiTagForm (operation) {
        var payload = {
           tags: [],
           cases: [],
           operation: operation
        };

        document.getElementById('multi-case-tag-assign-btn').disabled = true;
        document.getElementById('multi-case-tag-remove-btn').disabled = true;

        document.querySelectorAll('input[name^="select-case-"]:checked').forEach(function (input) {
            payload.cases.push(parseInt(input.value, 10));
        });
        document.querySelectorAll('input[name^="multi-case-tag-"]:checked').forEach(function (input) {
            payload.tags.push(parseInt(input.value, 10));
        });

        fetch(monitoringCaseTagsUpdateUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        }).then(function (response) {
            if (!response.ok) {
                return;
            }
            return response.json().catch(function () {
                return null;
            }).then(function (data) {
                if (response.status == 202) {
                    window.location.reload(true);
                } else {
                    alert('Something went wrong. Status code: ' + response.status + '.');
                    console.log(data, response.status, response);
                }
            });
        }).catch(function () {});
    }

    document.getElementById('multi-case-tag-assign-btn').addEventListener('click', function (event) {
        event.preventDefault();
        submitMultiTagForm(OPERATION_ADD);
    });

    document.getElementById('multi-case-tag-remove-btn').addEventListener('click', function (event) {
        event.preventDefault();
        submitMultiTagForm(OPERATION_REMOVE);
    });

    document.getElementById('multi-case-tag-select-all').addEventListener('change', function () {
        var checked = this.checked;

        document.querySelectorAll('input[name^="select-case-"]').forEach(function (input) {
            input.checked = checked;
        });
    });
});
