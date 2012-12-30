$(document).ready(function () {

    var window_h = $(window).height();
    var header_h = $('header').height();
    var footer_h = $('footer').height();

    var new_height = window_h - (header_h + footer_h);
    $('#content-wrapper').height(new_height);
});

$(window).resize(function () {
    var window_h = $(window).height();
    var header_h = $('header').height();
    var footer_h = $('footer').height();

    var new_height = window_h - (header_h + footer_h);
    $('#content-wrapper').height(new_height);
});