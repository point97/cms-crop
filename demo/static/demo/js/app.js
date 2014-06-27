angular.module('cropApp', [] )
    .config(function($httpProvider) {
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    
    }).controller('homepagectrl', ['$scope', function ($scope) {
        $scope.test ="WTF I'm a test";
}]);
