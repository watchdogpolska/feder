AjaxDatatableViewUtils.init({
    search_icon_html: '<i class="fa-solid fa-magnifying-glass"></i>',
    language: {
    },
    fn_daterange_widget_initialize: function(table, data) {
        var wrapper = table.closest('.dataTables_wrapper');
        var toolbar = wrapper.find(".toolbar");
        toolbar.html(
            '<div class="daterange" style="float: left; margin-right: 6px;">' +
                '<span class="from"><label>Ostatni list od</label>: ' +
                    '<input type="date" class="date_from datepicker"></span>' +
                '<span class="to"><label>&nbsp do</label>: ' +
                    '<input type="date" class="date_to datepicker"></span>' +
            '</div>'
        );
        toolbar.find('.date_from, .date_to').on('change', function(event) {
            // Annotate table with values retrieved from date widgets
            table.data('date_from', wrapper.find('.date_from').val());
            table.data('date_to', wrapper.find('.date_to').val());
            // Redraw table
            table.api().draw();
        });
    }
});

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
                    conf_yes: function() { return $("input[name='check_conf_yes']").is(":checked") ? 1 : 0; },
                    conf_no: function() { return $("input[name='check_conf_no']").is(":checked") ? 1 : 0; },
                    resp_yes: function() { return $("input[name='check_resp_yes']").is(":checked") ? 1 : 0; },
                    resp_no: function() { return $("input[name='check_resp_no']").is(":checked") ? 1 : 0; },
                    quar_yes: function() { return $("input[name='check_quar_yes']").is(":checked") ? 1 : 0; },
                    quar_no: function() { return $("input[name='check_quar_no']").is(":checked") ? 1 : 0; },
                    voivodeship_filter: function() { return $("select[name='voivodeship']").val(); },
                    county_filter: function() { return $("select[name='county']").val(); },
                    community_filter: function() { return $("select[name='community']").val(); },
                    tags_filter: function() { return $("select[name='tags']").val(); },
                },
            );
            $('.filters input, .filters button').on('change paste keyup click', function() {
                // redraw the table
                $('#' + DataTablesTableId).DataTable().ajax.reload(null, false);
            });
        }
    });
})(jQuery);
