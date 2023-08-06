angular.module('core')

.directive('byNumber', function() {
    return {
        require: 'ngModel',
        link: function(scope, element, attrs, ngModel) {
            ngModel.$parsers.push(function(val) {
                if (val === 'null') {
                    return null;
                } else {
                    return parseInt(val, 10);
                }
            });
            ngModel.$formatters.push(function(val) {
                if (angular.isUndefined(val) || val === null) {
                    return 'null';
                } else {
                    return '' + val;
                }
            });
        }
    };
});
