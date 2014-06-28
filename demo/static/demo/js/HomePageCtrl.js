angular.module('cropApp')
    .controller('HomePageCtrl', [  '$scope', '$route', '$routeParams', '$location', '$anchorScroll',
                                 function ($scope, $route, $routeParams, $location, $anchorScroll) {  
        $scope.test ="WTF I'm a test 2";
        
        $scope.$route = $route;
        $scope.$location = $location;
        $scope.$routeParams = $routeParams;

        $scope.topic = '';
        $scope.showDataCatalogs = false;
        $scope.showDataPriorities = false;


        $scope.$watch('$routeParams', function(newValue){
            console.log(newValue)
            if (newValue.section){
                $location.hash(newValue.section);
                $anchorScroll();
            }

        }, 'true');

        $scope.setTopic = function(topic){
            console.log(topic)
            $scope.topic = topic;
        }
}]);