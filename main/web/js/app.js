var modules = [
    'app.filters',
    'app.directives',
    'app.services',
    'app.controllers',
    'ngResource'
];

// Declare app level module
angular.module('app', modules)

.config(function ($routeProvider, $locationProvider) {
    $locationProvider.html5Mode(true);

    var snapshot_data = {
        templateUrl: '/partials/networktraffic/index.html',
        reloadOnSearch: false
    };

    var upload_data = {
        templateUrl: '/partials/networktraffic/snapshotupload.html'
    };

    $routeProvider.when('/networktraffic', snapshot_data)
                  .when('/networktraffic/upload', upload_data)
                  .otherwise({redirectTo: '/networktraffic'});
});