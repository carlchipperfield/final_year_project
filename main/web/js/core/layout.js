function resizecontent() {
    var window_h = $(window).height();
    var header_h = $('header').height();
    var footer_h = $('footer').height();
    var new_height = window_h - (header_h + footer_h);
    $('#content-wrapper').height(new_height);
}

$(document).ready(resizecontent);
$(window).resize(resizecontent);