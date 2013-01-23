var actions = {
    get: {method: 'GET'},
    list: {method: 'GET', isArray: true},
    remove: {method: 'DELETE'}
};

var app = angular.module('app', ['ngResource']);

app.config(function($routeProvider, $locationProvider){
    //$locationProvider.html5Mode(true);

    var snapshot_data = {
        templateUrl: '/partials/networktraffic.html',
        reloadOnSearch: false
    };

    var upload_data = {
        templateUrl: '/partials/snapshotupload.html'
    };

    $routeProvider.when('/networktraffic', snapshot_data)
                  .when('/networktraffic/upload', upload_data)
                  .otherwise({redirectTo: '/networktraffic'});
});

app.filter('formatdate', function() {
    return function(input) {
        var date = new Date(input);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };
});

app.filter('formatport', function() {
    return function(input) {
        if (input !== '') {
            return ':' + input;
        }
        return input;
    };
});

app.filter('capitalize', function() {
    return function(input) {
        if (!input) {
            return input;
        }
        return input.charAt(0).toUpperCase() + input.slice(1);
    };
});

/* Diective to resize the content wrapper */
app.directive('resize', function($timeout) {

    var directiveDefinitionObject = {
        compile: function compile() {
            return function postLink() {
                var header = $('header');
                var container = $('#content-wrapper');

                function resizeWrapper() {
                    container.height($(window).height() - header.height());
                }
                resizeWrapper();

                $(window).resize( function() {
                    resizeWrapper();
                });
            };
        }
    };
    return directiveDefinitionObject;
});


app.factory('mySharedService', function($rootScope) {

    var sharedService = {};
    this.snapshot = undefined;

    sharedService.displaySnapshot = function(snapshot) {
        this.snapshot = snapshot;
        $rootScope.$broadcast('displaysnapshot');
    };

    sharedService.removeSnapshot = function() {
        $rootScope.$broadcast('removesnapshot');
    };

    return sharedService;
});


function AppCtrl($scope, mySharedService) {
    $scope.page = {
        
    };
}


function SnapshotListCtrl($scope, $resource, mySharedService, $location, $routeParams, $window)
{
    var Snapshot = $resource('/api/snapshot/:id', {}, actions);

    this.process_snapshots = function() {
        var snapshot = {};

        if ($routeParams.id) {
            var found_snapshot = false;
            for (var i = 0; i < $scope.snapshots.length; i++) {
                if ($scope.snapshots[i]._id === $routeParams.id) {
                    found_snapshot = true;
                    snapshot = $scope.snapshots[i];
                    break;
                }
            }
            if (!found_snapshot) {
                $location.path('/#/networktraffic').replace();
            }
        }
        else if ($scope.snapshots.length > 0) {
            snapshot = $scope.snapshots[0];
        }

        mySharedService.displaySnapshot(snapshot);
    };

    $scope.display_snapshot = function(index) {
        var snapshot = $scope.snapshots[index];
        $location.search({id: snapshot._id});
        mySharedService.displaySnapshot(snapshot);
    };

    $scope.upload = function() {
        $window.location.href = '/#/networktraffic/upload';
    };

    $scope.$on('removesnapshot', function() {
        var snapshot_id = mySharedService.snapshot._id;

        for (var i = 0; i < $scope.snapshots.length; i++) {
            if ($scope.snapshots[i]._id === snapshot_id) {
                $scope.snapshots.splice(i, 1);
                break;
            }
        }

        if ($scope.snapshots.length === 0) {
            // Replace with empty object, which represents no snapshots
            mySharedService.displaySnapshot({});
        }
        else {
            i = (i > 0) ? i-- : i;
            mySharedService.displaySnapshot($scope.snapshots[i]);
        }

        
    });

    $scope.snapshots = Snapshot.list({}, this.process_snapshots);
}


function SnapshotCtrl($rootScope, $scope, $log, $resource, mySharedService)
{
    /*
        Work out how to document javascript!
        The snapshot should be in one of three states
            1. Loading (undefined)
            2. No Snapshot (empty object)
            3. Snapshot (snapshot object)
    */
    $rootScope.page = {
        title: 'Network Traffic'
    };

    $scope.snapshotViews = ['Information', 'Statistics', 'Network Messages'];
    $scope.activeSnapshotView = $scope.snapshotViews[0];

    $scope.messageviews = ['Information', 'Headers', 'Content'];
    $scope.currentmessageview = $scope.messageviews[0];

    var Snapshot = $resource('/api/snapshot/:id', {}, actions);
    var Messages = $resource('/api/snapshot/:id/networkmessages?limit=:limit', {}, actions);

    $scope.$on('displaysnapshot', function() {
        $scope.snapshot = mySharedService.snapshot;
        if ($scope.isSnapshot()) {
            $scope.retrieve_messages($scope.snapshot._id);
        }
    });

    $scope.remove = function() {
        var success = function () {
            mySharedService.removeSnapshot();
        };
        var fail = function() {
            $log.error('Delete Failed');
        };
        Snapshot.remove({id: $scope.snapshot._id}, success, fail);
    };

    $scope.retrieve_messages = function(snapshot_id) {
        console.log($scope.networkmessages);
        var url_params = {id: snapshot_id, limit: 30};
        $scope.networkmessages = Messages.list(url_params);
    };

    $scope.isSnapshot = function() {
        var snapshot = mySharedService.snapshot;
        return snapshot !== undefined && snapshot._id !== undefined;
    };

    $scope.isNoSnapshot = function() {
        var snapshot = mySharedService.snapshot;
        return snapshot !== undefined && snapshot._id === undefined;
    };
}



function UploadSnapshotCtrl($rootScope, $scope, $resource, $window)
{
    $rootScope.page = {
        title: 'Network Traffic Upload'
    };

    $scope.upload = function() {

        var formData = new FormData();
        formData.append('title', $scope.title);
        formData.append('description', $scope.desc);
        formData.append('logfile_name', $scope.filename);
        formData.append('logfile_content', $scope.logfile);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/snapshotupload', true);

        // Listen to the upload progress.
        var progressBar = document.querySelector('progress');
        xhr.upload.onprogress = function(e) {
          if (e.lengthComputable) {
            progressBar.value = (e.loaded / e.total) * 100;
            progressBar.textContent = progressBar.value;
          }
        };

        xhr.onload = function() {
            if (this.status === 200) {
                var url = '/#/networktraffic?id=' + this.responseText;
                $window.location.href = url;
            }
        };

        xhr.send(formData);
    };

    $scope.setFile = function(element) {
        $scope.$apply(function($scope) {
            $scope.filename = element.files[0].name;
            $scope.logfile = element.files[0];
        });
    };
}
