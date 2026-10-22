document.addEventListener('DOMContentLoaded', function() {
    const table1 = document.getElementById("datatable_monitorings");
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
            });
        });
        // Initialize table
        AjaxDatatableViewUtils.initialize_table(
            '#datatable_monitorings',
            "/monitoringi/monitorings_table_ajax_data/",
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
                scrollY: maxHeight - 250,
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
            },
        );
        // document.querySelectorAll('.filters input').forEach(function(el) {
        //     // redraw the table
        //     AjaxDatatableViewUtils.redraw_table('#datatable_letters');
        // });
    }
});
