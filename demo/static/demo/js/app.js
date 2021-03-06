angular.module('cropApp', ['ngRoute', 'ui.bootstrap', 'ngScrollSpy'] )
    .config(function($httpProvider, $routeProvider, $locationProvider) {
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    
        $routeProvider
           .when('/', {
            templateUrl: ' ',
            controller: 'HomPageCtrl',
          })
           .when('/:section', {
            template: ' ',
            controller: 'HomPageCtrl',
          })
           .when('/:section/:topic', {
            template: ' ',
            controller: 'HomPageCtrl',
          })

});
