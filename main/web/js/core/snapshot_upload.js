function SnapshotUploadCtrl($scope) {

    $scope.snapshotuploads = [
    ];
   
    $scope.uploadSnapshot = function() {

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
            progressBar.textContent = progressBar.value; // Fallback for unsupported browsers.
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