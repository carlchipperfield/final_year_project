myApp.controller('PaginationCtrl', function ($scope) {

    $scope.next = function () {
        if (!$scope.isLastPage()) {
            $scope.pagination.offset = $scope.pagination.offset + $scope.pagination.limit;
        }
    };

    $scope.previous = function () {
        if (!$scope.isFirstPage()) {
            $scope.pagination.offset = $scope.pagination.offset - $scope.pagination.limit;
        }
    };

    $scope.isFirstPage = function () {
        return $scope.pagination.offset === 0;
    };

    $scope.isLastPage = function () {
        return ($scope.pagination.offset + $scope.pagination.limit) > $scope.pagination.total;
    };

    $scope.isPaginated = function () {
        return $scope.pagination.total !== undefined &&
            $scope.pagination.total > $scope.pagination.limit;
    };
});