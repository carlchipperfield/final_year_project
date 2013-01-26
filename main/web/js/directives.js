angular.module('app.directives', [])

.directive('resize', function () {
    var directiveDefinitionObject = {
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
    return directiveDefinitionObject;
});