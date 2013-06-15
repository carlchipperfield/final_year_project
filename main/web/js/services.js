angular.module('app.services', [])

/*
    The following service allows controllers to share snapshot events
*/
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

    sharedService.querySnapshot = function (query) {
        this.query = query;
        $rootScope.$broadcast('querysnapshot');
    };

    sharedService.queryDialog = function (query) {
        this.querydialog = query;
        $rootScope.$broadcast('querydialog');
    };

    return sharedService;
})


/*
    The following service allows controllers to report errors to be displayed
    as a error message banner.
*/
.factory('errorService', function ($rootScope) {

    var errorService = {};

    errorService.reportError = function (title, message) {
        this.report('error', title, message);
    };

    errorService.reportSuccess = function (title, message) {
        this.report('success', title, message);
    };

    errorService.reportInfo = function (title, message) {
        this.report('info', title, message);
    };

    errorService.clearErrors = function () {
        $rootScope.$broadcast('clearerrors');
    };

    errorService.report = function (type, title, message) {
        errorService.error = {
            type:    type,
            title:   title,
            message: message
        };
        $rootScope.$broadcast('founderror');
    };

    return errorService;
});
