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
        templateUrl: '/partials/core/directives/navbar.html'
    };
})

.directive('networkmessage', function () {
    return {
        restrict: 'E',
        replace: true,
        controller: 'NetworkMessageCtrl',
        scope: {
            data: '=',
            index: '=',
            total: '=',
            offset: '='
        },
        templateUrl: '/partials/networktraffic/directives/networkmessage.html',
        link: function(scope, element, attrs) {
            // Need to identify the content type found in the headers
            var headers = scope.data.headers;

            for (var i = 0; i < headers.length; i++) {
                if (headers[i].name === 'Content-Type') {

                    var value = headers[i].value;

                    if (value.match(/.*xml.*/)) {
                        scope.data.contenttype = 'xml';
                    }
                    else if (value === 'application/sdp') {
                        scope.data.contenttype = 'sdp';
                    }
                    else {
                        scope.data.contenttype = 'none';
                    }

                    break;
                }
            }
        }
    };
})

.directive('sdp', function () {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            content: '='
        },
        templateUrl: '/partials/networktraffic/directives/sdpcontent.html',
        link: function(scope, element, attrs) {

            scope.sdp = new ContentFormatter().formatSDP(scope.content);
            var media = scope.sdp.media_descriptions;

            for (var i = 0; i < media.length; i++) {
                media[i].displayed = false;
            }
        }
    };
})

.directive('xmldoc', function ($compile) {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            doc: '='
        },
        templateUrl: '/partials/networktraffic/directives/xml.html',
        link: function(scope, element, attrs) {

            scope.xml = new ContentFormatter().formatXML(scope.doc);
        }
    };
})

.directive('xmlnode', function ($compile) {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            node: '='
        },
        templateUrl: '/partials/networktraffic/directives/xmlnode.html',
        compile: function(tElement, tAttr) {
            var contents = tElement.contents().remove();
            var compiledContents;
            return function(scope, iElement, iAttr) {
                if(!compiledContents) {
                    compiledContents = $compile(contents);
                }
                compiledContents(scope, function(clone, scope) {
                         iElement.append(clone);
                });
        };
    }
    };
});
