angular.module('app.filters', [])

.filter('formatdate', function () {
    return function (input) {
        if (input !== '') {
            var date = new Date(input);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        }
        return '-';
    };
})

.filter('formatport', function () {
    return function (input) {
        if (input !== '') {
            return ':' + input;
        }
        return input;
    };
})

.filter('capitalize', function () {
    return function (input) {
        if (!input) {
            return input;
        }
        return input.charAt(0).toUpperCase() + input.slice(1);
    };
});