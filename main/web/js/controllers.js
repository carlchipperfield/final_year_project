var actions = {
    get: {method: 'GET'},
    list: {method: 'GET'},
    update: {method: 'PUT'},
    remove: {method: 'DELETE'}
};

angular.module('app.controllers', [])

.controller('AppCtrl', function ($scope) {
    $scope.page = {};
})

.controller('ErrorCtrl', function ($scope, errorService) {

    // Maintain a list of errors that are displayed to the user
    $scope.errors = [];

    $scope.$on('founderror', function () {

        if ($scope.errors.length > 0) {
            // Make sure that the error is not already displayed to the user
            for (var i = 0; i < $scope.errors.length; i++) {
                var error = $scope.errors[i];
                if (error.title !== errorService.error.title ||
                    error.type !== errorService.error.type) {

                    // Push onto error list
                    $scope.errors.push(errorService.error);
                    break;
                }
            }
        }
        else {
            // No errors so just push onto list
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
    // Initialise the snapshot REST API to return all snapshots
    var Snapshot = $resource('/api/snapshot/:id', {}, actions);

    this.process_snapshots = function () {
        var snapshot = {};

        if ($routeParams.id) {
            // Attempt to find the snapshot referenced in url
            var found_snapshot = false;
            for (var i = 0; i < $scope.snapshots.snapshots.length; i++) {
                if ($scope.snapshots.snapshots[i]._id === $routeParams.id) {
                    found_snapshot = true;
                    snapshot = $scope.snapshots.snapshots[i];
                    break;
                }
            }
            if (!found_snapshot) {
                // Redirect to default snapshot
                $location.path('/#/networktraffic').replace();
            }
        }
        else if ($scope.snapshots.snapshots.length > 0) {
            // display the first snapshot
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
            // Find the snapshot with the correct id and remove from the list
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
            // Display previous snapshot if not the first snapshot deleted
            var new_index = (i > 0) ? i - 1: i;
            $location.search('id', $scope.snapshots.snapshots[new_index]._id);
            mySharedService.displaySnapshot($scope.snapshots.snapshots[new_index]);
        }
    });

    $scope.snapshots = Snapshot.list({}, this.process_snapshots);
})

.controller('DialogMessages', function ($scope, $resource, mySharedService)
{
    var Message = $resource('/api/snapshot/:id/networkmessages/:message_id', {}, actions);
    var message_ids = $scope.$parent.dialog.messages;

    $scope.messages = {
        messages: [],
        displayed: false,
        views: ['Details', 'Headers', 'Content'],
        sortby: 'utc'
    };

    $scope.toggleTag = function (message_index) {
        var message = $scope.messages.messages[message_index];
        var tagged = (message.tagged && message.tagged === 'true') ? 'false' : 'true';

        var success = function () {
            message.tagged = tagged;
        };

        var url_params = {
            id: mySharedService.snapshot._id,
            message_id: message._id
        };

        var msg = new Message();
        msg.tagged = tagged;
        msg.$update(url_params, success);
    };

    $scope.isTagged = function (message_index) {
        var message = $scope.messages.messages[message_index];
        return message.tagged && message.tagged === 'true';
    };

    $scope.toggleDisplayed = function () {

        if (!$scope.messages.displayed && $scope.messages.messages.length === 0) {

            var success = function (message) {
                message.view = $scope.messages.views[0];
                $scope.messages.messages.push(message);
            };

            for (var i = 0; i < message_ids.length; i++) {

                var url_params = {
                    id: mySharedService.snapshot._id,
                    message_id: message_ids[i]
                };

                Message.get(url_params, success);
            }
        }
        $scope.messages.displayed = !$scope.messages.displayed;
    };
})

.controller('SIPDialogs', function ($rootScope, $scope, $resource, mySharedService)
{
    // Set the two REST api resource requests
    var SIPDialogs = $resource('/api/snapshot/:id/sipdialogs?:query', {}, actions);

    $scope.query = '';
    $scope.networkmessages = [];

    $scope.retrieveDialogs = function (snapshot_id) {

        var url_params = {
            id: snapshot_id,
            query: $scope.query
        };
        $scope.dialogs = SIPDialogs.list(url_params);
    };

    $scope.$on('displaysnapshot', function () {
        $scope.getDialogs();
    });

    $scope.$on('querydialog', function () {
        $scope.query = mySharedService.querydialog;
        $scope.getDialogs();
    });

    $scope.isSnapshot = function () {
        var snapshot = mySharedService.snapshot;
        return snapshot !== undefined && snapshot._id !== undefined;
    };

    $scope.getDialogs = function () {
        $scope.snapshot = mySharedService.snapshot;

        if ($scope.isSnapshot()) {
            $scope.retrieveDialogs($scope.snapshot._id);
        }
    };

    $scope.getDialogs(); // Init manually
})


.controller('TaggedMessages', function ($scope, mySharedService, $resource) {

    var Messages = $resource('/api/snapshot/:id/networkmessages?tagged=true', {}, actions);
    var Message = $resource('/api/snapshot/:id/networkmessages/:netid', {id: '@id', netid: '@netid'}, {save: {method: 'PUT'}});

    $scope.$on('displaysnapshot', function () {
        $scope.retrieve_messages();
    });

    $scope.isMessages = function () {
        return $scope.networkmessages.networkmessages && $scope.networkmessages.networkmessages.length > 0;
    };

    $scope.retrieve_messages = function () {
        var url_params = {
            id: mySharedService.snapshot._id
        };
        $scope.networkmessages = Messages.list(url_params);
    };

    $scope.Untag = function (message_id) {
        var url_params = {
            id: $scope.snapshot._id,
            netid: message_id
        };
        var success = function () {
            var networkmessages = $scope.networkmessages.networkmessages;
            for (var i = 0; i < networkmessages.length; i++) {
                if (networkmessages[i]._id === message_id) {
                    networkmessages.splice(i, 1);
                    break;
                }
            }
        };
        var msg = new Message();
        msg.tagged = 'false';
        msg.$save(url_params, success);
    };

    $scope.retrieve_messages();
})

.controller('DialogFilter', function ($scope, mySharedService) {

    $scope.filterFields = [
        {'display': 'call-id', 'field': 'call_id', 'list': 'call-ids'},
        {'display': 'participants', 'field': 'participants', 'list': 'participants', 'filters': ['sender', 'receiver']}
    ];

    $scope.filter = {};
    $scope.snapshot = mySharedService.snapshot;

    $scope.$on('displaysnapshot', function () {
        $scope.filter = {};
        $scope.snapshot = mySharedService.snapshot;
    });

    $scope.getFieldValues = function (field) {
        return $scope.snapshot.summary[field];
    };

    $scope.setFilter = function (field, value) {
        if ($scope.filter[field] === undefined) {
            // Insert the new field as an array
            $scope.filter[field] = [value];
        }
        else {
            var index = $scope.filter[field].indexOf(value);
            if (index === -1) {
                // Value is being added to the query
                $scope.filter[field].push(value);
            }
            else {
                // Value is being removed from the query
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
        mySharedService.queryDialog($scope.composeQuery());
    };

    $scope.clear = function () {
        // Will remove any filters and save
        $scope.filter = {};
        mySharedService.queryDialog('');
    };

    $scope.composeQuery = function () {
        // Concat all the options
        var query = '';
        var field;
        for (field in $scope.filter) {

            if (typeof $scope.filter[field] !== 'function') {
                if ($scope.filter[field].length > 0) {

                    var fields = [field];

                    for (var i = 0; i < $scope.filterFields.length; i++) {
                        if (typeof $scope.filterFields[i] !== 'function') {
                            if ($scope.filterFields[i]['field'] === field) {
                                if ($scope.filterFields[i]['filters']) {
                                    fields = $scope.filterFields[i]['filters'];
                                }
                            }
                        }
                    }

                    for (i = 0; i < fields.length; i++) {
                        if (typeof fields[i] !== 'function') {
                            query += '&' + fields[i] + '=';
                            for (var j = 0; j < $scope.filter[field].length; j++) {
                                query += (j === 0) ? $scope.filter[field][j] : ' OR ' + $scope.filter[field][j];
                            }
                        }
                    }
                }
            }
        }

        return query;
    };
})

.controller('SnapshotComments', function ($scope, $resource, mySharedService, errorService)
{
    var Notes = $resource('/api/snapshot/:id/notes', {}, actions);
    var Note = $resource('/api/snapshot/:id/notes/:note_id', {}, actions);

    $scope.$on('displaysnapshot', function () {
        $scope.retrieveNotes();
    });

    $scope.retrieveNotes = function () {
        if (mySharedService.snapshot) {
            var params = {'id': mySharedService.snapshot._id};
            $scope.notes = Notes.list(params);
        }
    };

    $scope.isComments = function () {
        if ($scope.notes && $scope.notes.notes) {
            for (var i = 0; i < $scope.notes.notes.length; i++) {
                if (!$scope.notes.notes[i].removed) {
                    return true;
                }
            }
        }
        return false;
    };

    $scope.add = function (note) {

        var newNote = angular.copy(note);

        var success = function (retrievedNote) {
            $scope.notes.notes.push(retrievedNote);
            note.note = ''; // Reset the add note field
            errorService.clearErrors();
        };

        var fail = function () {
            errorService.reportError('', 'Failed to add new note');
        };

        if (note.note !== '') {
            var notes = new Notes();
            notes.note = newNote.note;
            var params = {id: $scope.snapshot._id};
            notes.$update(params, success, fail);
        }
    };

    var inProgress = {};

    $scope.remove = function (note_id) {

        if (isInProgress(note_id)) {
            return false;
        }
        inProgress[note_id] = true;

        var params = {
            'id': mySharedService.snapshot._id,
            'note_id': note_id
        };

        var success = function () {

            for (var i = 0; i < $scope.notes.notes.length; i++) {
                if ($scope.notes.notes[i]._id === note_id) {
                    $scope.notes.notes[i].removed = true;
                    break;
                }
            }
            delete inProgress[note_id];
            errorService.clearErrors();
        };

        var fail = function () {
            delete inProgress[note_id];
            errorService.reportError('', 'Failed to remove note.');
        };

        Note.remove(params, success, fail);
    };

    var isInProgress = function (resource_id) {
        
        if (resource_id in inProgress) {
            return true;
        }
        return false;
    };

    $scope.toggleNoteActions = function (index) {
        var note = $scope.notes.notes[index];
        note.controls = !note.controls;
    };

    $scope.retrieveNotes();
})

.controller('SnapshotCtrl', function ($rootScope, $scope, $resource, mySharedService, errorService)
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

    // Set state that tracks the current snapshot view
    $scope.snapshotViews = ['Details', 'Statistics', 'SIP Dialogs', 'Network Messages', 'Tagged'];
    $scope.activeSnapshotView = $scope.snapshotViews[0];

    // Set state that tracks message view, each message has unique value in scope
    $scope.messageviews = ['Details', 'Headers', 'Content'];
    $scope.currentmessageview = $scope.messageviews[0];

    $scope.commentsDisplayed = false;
    $scope.filterDisplayed = false;

    $scope.query = ''; // No query by default

    // Set the two REST api resource requests
    var Snapshot = $resource('/api/snapshot/:id', {}, actions);
    var Messages = $resource('/api/snapshot/:id/networkmessages?limit=:limit&offset=:offset:query', {}, actions);
    var Message = $resource('/api/snapshot/:id/networkmessages/:netid', {id: '@id', netid: '@netid'}, {save: {method: 'PUT'}});

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

            // Reset the query
            $scope.query = '';

            $scope.retrieve_messages($scope.snapshot._id);
        }
    });

    $scope.toggleFilter = function () {
        // opens and closes the filter form
        $scope.filterDisplayed = !$scope.filterDisplayed;
    };

    $scope.toggleComments = function () {
        // opens and closes the filter form
        $scope.commentsDisplayed = !$scope.commentsDisplayed;
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
            // publish the remove of the current snapshot
            mySharedService.removeSnapshot();
            // remove existing errors
            errorService.clearErrors();
        };
        var fail = function () {
            // display remove failed error
            errorService.reportError('', 'Failed to delete network traffic snapshot');
        };
        Snapshot.remove({id: $scope.snapshot._id}, success, fail);
    };

    $scope.retrieve_messages = function (snapshot_id) {
        // Send request to server for current list of network messages
        var url_params = {
            id: snapshot_id,
            limit: $scope.limit,
            offset: $scope.offset,
            query: $scope.query
        };

        $scope.networkmessages = Messages.list(url_params);
    };

    $scope.toggleTag = function (message_id, tag) {
        var url_params = {
            id: $scope.snapshot._id,
            netid: message_id
        };
        var success = function () {
            var networkmessages = $scope.networkmessages.networkmessages;
            for (var i = 0; i < networkmessages.length; i++) {
                if (networkmessages[i]._id === message_id) {
                    networkmessages[i].tagged = tag;
                }
            }
        };
        var msg = new Message();
        msg.tagged = tag;
        msg.$save(url_params, success);
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
        {'display': 'call-id', 'field': 'call-id', 'list': 'call-ids'},
        {'display': 'method', 'field': 'method', 'list': 'methods'}
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
            // Insert the new field as an array
            $scope.filter[field] = [value];
        }
        else {
            var index = $scope.filter[field].indexOf(value);
            if (index === -1) {
                // Value is being added to the query
                $scope.filter[field].push(value);
            }
            else {
                // Value is being removed from the query
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

        // Create form data object containing the form fields
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
                // If successful redirect to the snapshot analysis page
                $location.path('/networktraffic');
                $location.search('id', this.responseText);
                $scope.$apply();
            }
            else {
                // Report error
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
