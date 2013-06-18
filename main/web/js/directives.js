angular.module('app.directives', [])

.directive('resize', function () {
    return {
        compile: function compile() {
            return function postLink() {
                var header = $('header');
                var container = $('#content-wrapper');

                function resizeWrapper() {
                    container.height($(window).height() - header.height());
                }
                resizeWrapper();

                $(window).resize(function () {
                    resizeWrapper();
                });
            };
        }
    };
})

.directive('navbar', function () {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            navdata: '=',
            direction: '@direction',
            active: '='
        },
        templateUrl: '/partials/core/navbar.html'
    };
});