function mySlowMove() {
    var div = document.getElementById("start");
    var distance = div.offsetTop;
    asyncLoop(distance);
}

async function asyncLoop(distance) {

    for (var i = 1; i < 101; i++) {
        window.scrollTo(0, i / 100 * distance);
        await new Promise(resolve => setTimeout(resolve, 5));
    }

}


$(document).ready(function(){
$("#mytable #checkall").click(function () {
        if ($("#mytable #checkall").is(':checked')) {
            $("#mytable input[type=checkbox]").each(function () {
                $(this).prop("checked", true);
            });

        } else {
            $("#mytable input[type=checkbox]").each(function () {
                $(this).prop("checked", false);
            });
        }
    });

    $("[data-toggle=tooltip]").tooltip();
});
