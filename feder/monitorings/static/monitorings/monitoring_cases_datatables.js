;(function($) {
    $(function() {
        const table1 = document.getElementById(DataTablesTableId);
        if (table1) {
            var tableTop = $("#tableWrapper")[0].getBoundingClientRect().top;
            var viewportHeight = $(window).innerHeight();
            var maxHeight = viewportHeight - tableTop;
            $("#tableWrapper").css({
                maxHeight: maxHeight - 0,
            });
            // Subscribe "initComplete" event
            $('#' + DataTablesTableId).on('initComplete', function(event, table ) {
                // Code to resize input fields
                const tableWrapper = $("#tableWrapper");
                const headerCells = tableWrapper.find("th");
                headerCells.each(function() {
                    const input = $(this).find("input[type=text]");
                    $(this).css("padding", "0");
                    input.css("width", "100%");
                    input.css("box-sizing", "border-box");
                    const select = $(this).find("select");
                    select.css("box-sizing", "border-box");                    
                    select.css("width", "100%");
                });
            });
            // Initialize table
            AjaxDatatableViewUtils.initialize_table(
                $('#' + DataTablesTableId),
                AjaxDataURL,
                {
                    // extra_options (example)
                    processing: true,
                    serverSide: true,
                    autoWidth: true,
                    full_row_select: false,
                    scrollX: true,
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
            // $('.filters input').on('change paste keyup', function() {
            //     // redraw the table
            //     $('#datatable_letters').DataTable().ajax.reload(null, false);
            // });
        }
    });
})(jQuery);
