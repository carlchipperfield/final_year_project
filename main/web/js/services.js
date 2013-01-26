
angular.module('app.services', [])

.factory('mySharedService', function ($rootScope) {

    var sharedService = {};
    this.snapshot = undefined;

    sharedService.displaySnapshot = function (snapshot) {
        this.snapshot = snapshot;
        $rootScope.$broadcast('displaysnapshot');
    };

    sharedService.removeSnapshot = function () {
        $rootScope.$broadcast('removesnapshot');
    };

    return sharedService;
});