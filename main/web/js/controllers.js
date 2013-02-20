var actions = {
    get: {method: 'GET'},
    list: {method: 'GET'},
    remove: {method: 'DELETE'}
};

angular.module('app.controllers', [])


.controller('AppCtrl', function ($scope) {
    $scope.page = {};
})

.controller('ErrorCtrl', function ($scope, errorService) {
    $scope.errors = [];

    $scope.$on('founderror', function () {

        if ($scope.errors.length > 0) {
            for (var i = 0; i < $scope.errors.length; i++) {
                var error = $scope.errors[i];
                if (error.title !== errorService.error.title ||
                    error.type !== errorService.error.type) {
                    $scope.errors.push(errorService.error);
                    break;
                }
            }
        }
        else {
            $scope.errors.push(errorService.error);
        }
    });

    $scope.$on('clearerrors', function () {
        $scope.errors = [];
    });

    $scope.removeError = function (index) {
        $scope.errors.splice(index, 1);
    };
})

.controller('SnapshotListCtrl', function ($scope, $resource, mySharedService, $location, $routeParams, $window)
{
    var Snapshot = $resource('/api/snapshot/:id', {}, actions);

    this.process_snapshots = function () {
        var snapshot = {};

        if ($routeParams.id) {
            var found_snapshot = false;
            for (var i = 0; i < $scope.snapshots.snapshots.length; i++) {
                if ($scope.snapshots.snapshots[i]._id === $routeParams.id) {
                    found_snapshot = true;
                    snapshot = $scope.snapshots.snapshots[i];
                    break;
                }
            }
            if (!found_snapshot) {
                $location.path('/#/networktraffic').replace();
            }
        }
        else if ($scope.snapshots.snapshots.length > 0) {
            snapshot = $scope.snapshots.snapshots[0];
        }

        mySharedService.displaySnapshot(snapshot);
    };

    $scope.display_snapshot = function (index) {
        var snapshot = $scope.snapshots.snapshots[index];
        $location.path('/networktraffic');
        $location.search({id: snapshot._id});
        mySharedService.displaySnapshot(snapshot);
    };

    $scope.upload = function () {
        $window.location.href = '/#/networktraffic/upload';
    };

    $scope.$on('removesnapshot', function () {
        var snapshot_id = mySharedService.snapshot._id;

        for (var i = 0; i < $scope.snapshots.snapshots.length; i++) {
            if ($scope.snapshots.snapshots[i]._id === snapshot_id) {
                $scope.snapshots.snapshots.splice(i, 1);
                break;
            }
        }

        if ($scope.snapshots.snapshots.length === 0) {
            // Replace with empty object, which represents no snapshots
            mySharedService.displaySnapshot({});
        }
        else {
            var new_index = (i > 0) ? i - 1: i;
            $location.search('id', $scope.snapshots.snapshots[new_index]._id);
            mySharedService.displaySnapshot($scope.snapshots.snapshots[new_index]);
        }
    });
    $scope.snapshots = Snapshot.list({}, this.process_snapshots);
})


.controller('SnapshotCtrl', function ($rootScope, $scope, $log, $resource, mySharedService, errorService)
{
    /*
        Work out how to document javascript!
        The snapshot should be in one of three states
            1. Loading (undefined)
            2. No Snapshot (empty object)
            3. Snapshot (snapshot object)
    */
    $rootScope.page = {
        title: 'Network Traffic Analytics'
    };

    $scope.snapshotViews = ['Details', 'Statistics', 'Network Messages'];
    $scope.activeSnapshotView = $scope.snapshotViews[0];

    $scope.messageviews = ['Details', 'Headers', 'Content'];
    $scope.currentmessageview = $scope.messageviews[0];

    $scope.filterDisplayed = false;

    $scope.query = '';

    var Snapshot = $resource('/api/snapshot/:id', {}, actions);
    var Messages = $resource('/api/snapshot/:id/networkmessages?limit=:limit&offset=:offset:query', {}, actions);

    /* Pagination data */
    $scope.currentPage = 0;
    $scope.limit = 40;
    $scope.offset = 0;

    $scope.$on('displaysnapshot', function () {
        $scope.snapshot = mySharedService.snapshot;
        if ($scope.isSnapshot()) {

            // Reset the pagination data
            $scope.offset = 0;
            $scope.currentPage = 0;
            $scope.retrieve_messages($scope.snapshot._id);
        }
    });

    $scope.toggleFilter = function () {
        $scope.filterDisplayed = !$scope.filterDisplayed;
    };

    $scope.$on('querysnapshot', function () {
        // Reset the pagination data
        $scope.offset = 0;
        $scope.currentPage = 0;
        $scope.query = mySharedService.query;
        $scope.retrieve_messages($scope.snapshot._id);
    });

    $scope.remove = function () {
        var success = function () {
            mySharedService.removeSnapshot();
            errorService.clearErrors();
        };
        var fail = function () {
            errorService.reportError('', 'Failed to delete network traffic snapshot');
        };
        Snapshot.remove({id: $scope.snapshot._id}, success, fail);
    };

    $scope.retrieve_messages = function (snapshot_id) {
        var url_params = {
            id: snapshot_id,
            limit: $scope.limit,
            offset: $scope.offset,
            query: $scope.query
        };
        $scope.networkmessages = Messages.list(url_params);
    };

    $scope.isSnapshot = function () {
        var snapshot = mySharedService.snapshot;
        return snapshot !== undefined && snapshot._id !== undefined;
    };

    $scope.isNoSnapshot = function () {
        var snapshot = mySharedService.snapshot;
        return snapshot !== undefined && snapshot._id === undefined;
    };

    $scope.isMessages = function () {
        return $scope.networkmessages.networkmessages !== undefined &&
                $scope.networkmessages.networkmessages.length > 0 &&
                !$scope.inprogress;
    };

    $scope.next = function () {
        var offset = ($scope.currentPage + 1) * $scope.limit;

        if (offset < $scope.networkmessages.total) {
            $scope.currentPage++;
            $scope.offset = offset;
            $scope.retrieve_messages($scope.snapshot._id);
        }
    };

    $scope.previous = function () {
        if ($scope.currentPage > 0) {
            $scope.currentPage--;
            $scope.offset = $scope.currentPage * $scope.limit;
            $scope.retrieve_messages($scope.snapshot._id);
        }
    };

    $scope.isFirstPage = function () {
        return $scope.currentPage === 0;
    };

    $scope.isLastPage = function () {
        return (($scope.currentPage + 1) *
            $scope.limit) > ($scope.networkmessages.total);
    };

    $scope.isResponse = function (name) {
        return $scope.snapshot.statistics.responses[name] > 0;
    };
})


.controller('SnapshotFilter', function ($scope, mySharedService) {

    $scope.filterFields = [
        {'field': 'call-id', 'list': 'call-ids'},
        {'field': 'method', 'list': 'methods'}
    ];

    $scope.filter = {}; // Need to get data from server when persistent
    $scope.snapshot = mySharedService.snapshot;

    $scope.$on('displaysnapshot', function () {
        $scope.filter = {}; // Need to get data from server when persistent
        $scope.snapshot = mySharedService.snapshot;
    });

    $scope.getFieldValues = function (field) {
        return $scope.snapshot.summary[field];
    };

    $scope.setFilter = function (field, value) {
        if ($scope.filter[field] === undefined) {
            $scope.filter[field] = [value];
        }
        else {
            var index = $scope.filter[field].indexOf(value);
            if (index === -1) {
                $scope.filter[field].push(value);
            }
            else {
                $scope.filter[field].splice(index, 1);
            }
        }
    };

    $scope.isChecked = function (field, value) {
        return $scope.filter[field] !== undefined &&
            $scope.filter[field].indexOf(value) !== -1;
    };

    $scope.save = function () {
        // Will save the data at this point
        mySharedService.querySnapshot($scope.composeQuery());
    };

    $scope.clear = function () {
        // Will remove any filters and save
        $scope.filter = {};
        mySharedService.querySnapshot('');
    };

    $scope.composeQuery = function () {
        // Concat all the options
        var query = '';
        var field;
        for (field in $scope.filter) {

            if (typeof $scope.filter[field] !== 'function') {
                if ($scope.filter[field].length > 0) {

                    query += '&' + field + '=';
                    for (var i = 0; i < $scope.filter[field].length; i++) {
                        query += (i === 0) ? $scope.filter[field][i] : ' OR ' + $scope.filter[field][i];
                    }
                }
            }
        }

        return query;
    };
})

.controller('UploadSnapshotCtrl',
    function ($rootScope, $scope, $resource, $window, errorService, $location)
{
    $rootScope.page = {
        title: 'Network Traffic Upload'
    };

    $scope.$on('$destroy', function () {
        errorService.clearErrors();
    });

    $scope.cancelUpload = function () {
        $location.path('/networktraffic');
    };

    $scope.upload = function () {


        var formData = new FormData();
        if ($scope.title) {
            formData.append('title', $scope.title);
        }
        if ($scope.desc) {
            formData.append('description', $scope.desc);
        }
        if ($scope.filename) {
            formData.append('logfile_name', $scope.filename);
        }
        if ($scope.logfile) {
            formData.append('logfile_content', $scope.logfile);
        }

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/snapshotupload', true);

        // Listen to the upload progress.
        var progressBar = document.querySelector('progress');
        xhr.upload.onprogress = function (e) {
            if (e.lengthComputable) {
                progressBar.value = (e.loaded / e.total) * 100;
                progressBar.textContent = progressBar.value;
            }
        };

        xhr.onload = function () {
            if (this.status === 200) {
                $location.path('/networktraffic');
                $location.search('id', this.responseText);
                $scope.$apply();
            }
            else {
                progressBar.value = 0;
                errorService.reportError('Failed to upload diagnostics logfile.', '');
                $scope.$apply();
            }
        };

        xhr.send(formData);
    };

    $scope.setFile = function (element) {
        $scope.$apply(function ($scope) {
            $scope.filename = element.files[0].name;
            $scope.logfile = element.files[0];
        });
    };
});
