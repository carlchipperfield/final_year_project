var app = angular.module('app', ['ngResource']);

app.config(function($routeProvider, $locationProvider){
        //$locationProvider.html5Mode(true);

        var snapshot_data = {
            templateUrl: '/partials/snapshots.html',
            controller: 'SnapshotsCtrl'
        };

        var upload_data = {
            templateUrl: '/partials/upload.html',
            controller: 'UploadSnapshotCtrl'
        };

        $routeProvider.when('/snapshot/:id', snapshot_data)
                      .when('/snapshot', snapshot_data)
                      .when('/upload', upload_data)
                      .otherwise({redirectTo: '/snapshot'});
    });

app
.filter('formatdate', function() {
    return function(input) {
        var date = new Date(input);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };
})
.filter('formatport', function() {
    return function(input) {
        if (input === '') {
            return '';
        }
        else {
            return ':' + input;
        }
    };
});


var actions = {
        get: {method: 'GET'},
        list: {method: 'GET', isArray: true},
        remove: {method: 'DELETE'}
};


function SnapshotsCtrl($scope, $resource, $location, $routeParams)
{
    $scope.snapshotviews = ['Information', 'Statistics', 'Network Messages'];
    $scope.currentview = $scope.snapshotviews[0];

    $scope.messageviews = ['Information', 'Headers', 'Content'];
    $scope.currentmessageview = $scope.snapshotviews[0];

    $scope.remove = function(index) {
        var snapshot_id = $scope.snapshots[index]._id;
        Snapshot.remove({id: snapshot_id});
        $scope.snapshots.splice(index, 1);
    };

    $scope.retrieve_snapshot = function(snapshot_id) {
        var url = '/api/snapshot/:id';
        var url_params = {id: snapshot_id};
        var Messages = $resource(url, url_params, actions);
        $scope.currentsnapshot = Messages.get();
    };

    $scope.retrieve_messages = function(snapshot_id) {
        var url = '/api/snapshot/:id/networkmessages?limit=:limit';
        var url_params = {
            id: snapshot_id,
            limit: 30
        };
        var Messages = $resource(url, url_params, actions);
        $scope.networkmessages = Messages.list();
    };

    $scope.display_snapshot_detailed = function(index) {
        $scope.currentsnapshot = $scope.snapshots[index];
        $scope.retrieve_messages($scope.currentsnapshot._id);
    };

    $scope.display_snapshot_detailed_onload = function() {
        $scope.totalsnapshots = $scope.snapshots.length;

        // Load the snapshot messages from the server
        if ($routeParams.id) {
            // Load messages for snapshot in url
            $scope.retrieve_snapshot($routeParams.id);
            $scope.retrieve_messages($routeParams.id);
        }
        else {
            if ( $scope.snapshots.length > 0 ) {
                $scope.display_snapshot_detailed(0);
            }
        }
    };

    // Load snapshots from server
    var Snapshot = $resource('/api/snapshot/:id', {}, actions);
    $scope.snapshots = Snapshot.list({}, $scope.display_snapshot_detailed_onload);
}


function UploadSnapshotCtrl($scope)
{
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

        xhr.send(formData);
    };

    $scope.setFile = function(element) {
        $scope.$apply(function($scope) {
            $scope.filename = element.files[0].name;
            $scope.logfile = element.files[0];
        });
    };
}
