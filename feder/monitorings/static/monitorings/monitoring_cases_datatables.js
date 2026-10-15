AjaxDatatableViewUtils.init({
    search_icon_html: '<i class="fa-solid fa-magnifying-glass"></i>',
    language: {
    },
    fn_daterange_widget_initialize: function(tableEl, data, api, extraFilterState) {
        var wrapper = tableEl.closest('.dt-container');
        var toolbar = wrapper.querySelector(".toolbar");
        toolbar.innerHTML =
            '<div class="daterange" style="float: left; margin-right: 6px;">' +
                '<span class="from"><label>Ostatni list od</label>: ' +
                    '<input type="date" class="date_from datepicker"></span>' +
                '<span class="to"><label>&nbsp do</label>: ' +
                    '<input type="date" class="date_to datepicker"></span>' +
            '</div>';
        toolbar.querySelectorAll('.date_from, .date_to').forEach(function(el) {
            el.addEventListener('change', function(event) {
                // Annotate table with values retrieved from date widgets
                extraFilterState.date_from = toolbar.querySelector('.date_from').value;
                extraFilterState.date_to = toolbar.querySelector('.date_to').value;
                // Redraw table
                api.draw();
            });
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const table1 = typeof DataTablesTableId !== 'undefined' ? document.getElementById(DataTablesTableId) : null;
    if (table1) {
        const tableWrapper = document.getElementById("tableWrapper");
        var tableTop = tableWrapper.getBoundingClientRect().top;
        var viewportHeight = window.innerHeight;
        var maxHeight = viewportHeight - tableTop;
        tableWrapper.style.maxHeight = (maxHeight - 0) + "px";
        // Subscribe "initComplete" event
        table1.addEventListener('initComplete', function(event) {
            // Code to resize input fields (only the column-filter row, not the sort-header row)
            tableWrapper.querySelectorAll("tr.datatable-column-filter-row th").forEach(function(th) {
                th.style.padding = "0";
                th.querySelectorAll("input[type=text]").forEach(function(input) {
                    input.style.width = "100%";
                    input.style.boxSizing = "border-box";
                });
                th.querySelectorAll("select").forEach(function(select) {
                    select.style.boxSizing = "border-box";
                    select.style.width = "100%";
                });
            });
            // The scrollY passed at init time (maxHeight - TableHeightMargin) was only
            // a guess made before any of the table's own chrome had actually rendered -
            // in particular the date-range toolbar (populated because this view has
            // get_latest_by set), which monitorings_table doesn't have and no fixed
            // margin constant accounts for. Now that the chrome above/below the
            // scrollable body is real DOM, measure it and resize the body to whatever
            // space is actually left, so the info/pagination row stays inside the
            // viewport instead of being pushed past it.
            var scrollBody = tableWrapper.querySelector(".dt-scroll-body");
            var controlsRows = tableWrapper.querySelectorAll(".datatable-controls-row");
            var bottomRow = controlsRows[controlsRows.length - 1];
            if (scrollBody && bottomRow) {
                var scrollBodyRectBefore = scrollBody.getBoundingClientRect();
                var chromeAboveBody = scrollBodyRectBefore.top - tableTop;
                // Distance from the body's (still unadjusted) bottom edge to the end of
                // the info/pagination row - covers the empty ".dt-scroll-foot" spacer
                // too, not just the row's own height.
                var chromeBelowBody = bottomRow.getBoundingClientRect().bottom - scrollBodyRectBefore.bottom;
                var available = maxHeight - chromeAboveBody - chromeBelowBody;
                scrollBody.style.height = available + "px";
                scrollBody.style.maxHeight = available + "px";
            }
        });
        // Initialize table
        AjaxDatatableViewUtils.initialize_table(
            '#' + DataTablesTableId,
            AjaxDataURL,
            {
                // extra_options (example)
                processing: true,
                serverSide: true,
                autoWidth: true,
                full_row_select: false,
                scrollX: true,
                // length selector (left) and generic search (right) on the same row;
                // info (left) and paging (right) on the same row
                dom: '<"toolbar"><"datatable-controls-row"lf>rt<"datatable-controls-row"ip>',
                // searching: false,
                scrollY: maxHeight - TableHeightMargin,
                // TODO make fixedColumns working !!!
                // fixedColumns: {
                //     left: 1,
                //     // right: 1
                // },
                "language": {
                    "processing":     "Przetwarzanie...",
                    "search":         "Szukaj:",
                    "lengthMenu":     "Pokaż _MENU_ pozycji",
                    "info":           "Pozycje od _START_ do _END_ z _TOTAL_ łącznie",
                    "infoEmpty":      "Pozycji 0 z 0 dostępnych",
                    "infoFiltered":   "(filtrowanie spośród _MAX_ dostępnych pozycji)",
                    "infoPostFix":    "",
                    "loadingRecords": "Wczytywanie...",
                    "zeroRecords":    "Nie znaleziono pasujących pozycji",
                    "emptyTable":     "Brak danych",
                    "paginate": {
                        "first":      "Pierwsza",
                        "previous":   "Poprzednia",
                        "next":       "Następna",
                        "last":       "Ostatnia"
                    },
                    "aria": {
                        "sortAscending": ": aktywuj, by posortować kolumnę rosnąco",
                        "sortDescending": ": aktywuj, by posortować kolumnę malejąco"
                    }
                },
            }, {
                // extra_data
                conf_yes: function() { return document.querySelector("input[name='check_conf_yes']").checked ? 1 : 0; },
                conf_no: function() { return document.querySelector("input[name='check_conf_no']").checked ? 1 : 0; },
                resp_yes: function() { return document.querySelector("input[name='check_resp_yes']").checked ? 1 : 0; },
                resp_no: function() { return document.querySelector("input[name='check_resp_no']").checked ? 1 : 0; },
                quar_yes: function() { return document.querySelector("input[name='check_quar_yes']").checked ? 1 : 0; },
                quar_no: function() { return document.querySelector("input[name='check_quar_no']").checked ? 1 : 0; },
                voivodeship_filter: function() { return document.querySelector("select[name='voivodeship']").value; },
                county_filter: function() { return document.querySelector("select[name='county']").value; },
                community_filter: function() { return document.querySelector("select[name='community']").value; },
                tags_filter: function() { return document.querySelector("select[name='tags']").value; },
            },
        );
        document.querySelectorAll('.filters input, .filters button').forEach(function(el) {
            ['change', 'paste', 'keyup', 'click'].forEach(function(evt) {
                el.addEventListener(evt, function() {
                    // redraw the table
                    AjaxDatatableViewUtils.redraw_table('#' + DataTablesTableId);
                });
            });
        });
    }
});
