angular.module('app.filters', [])

.filter('formatdate', function () {
    return function (input) {
        if (input !== '') {
            return moment(input).format('DD MMM YYYY HH:mm:ss');
        }
        return '-';
    };
})

.filter('precisedate', function () {
    return function (input) {
        if (input !== '') {
            return moment(input).format('DD MMM YYYY HH:mm:ss.SSS');
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
})

.filter('formatxml', function () {
    return function (input) {
        if (input !== '') {
            return ':' + input;
        }
        return input;
    };
});