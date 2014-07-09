angular.module('cropApp')
    .controller('HomePageCtrl', [  '$scope', function ($scope) {
        $scope.test ="WTF I'm a test 2";

        $scope.topics = {};
        $scope.topics.active = '';
        $scope.topics.slugs = _.map(angular.element(".topic-menu-item"), function(el){
            return $(el).attr("id");
        });

        $scope.showDataCatalogs = false;
        $scope.showDataPriorities = false;

        $scope.setTopic = function(topic){
            console.log("Changing to "+topic);
            $scope.topics.active = topic;
            console.log($scope.topics.active);

        };

        $scope.$on('slideChange', function(rs, index){
            var topic_slug = angular.element(".topic-menu-item").eq(index).attr("id");
            $scope.setTopic(topic_slug);
        });

        $scope.$watch('topics.activeTopic', function(newValue){
            console.log("[HomeCtrl]" + newValue)
        });

}]);