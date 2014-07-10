angular.module('cropApp')
    .controller('HomePageCtrl', [  '$scope', '$http', function ($scope, $http) {
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

        // $scope.$watch('topics.activeTopic', function(newValue){
        //     console.log("[HomeCtrl]" + newValue)
        // });

        $scope.get_events = function(date) {
            var url = '/api/v1/event/?format=json'
            if ($scope.cal.range[0] && $scope.cal.range[1]) {
                var strString = $scope.cal.range[0].toISOString().split('T')[0];
                var endString = $scope.cal.range[1].toISOString().split('T')[0];
                url += '&date_from__gte=' + strString + '&date_from__lte=' + endString;

            } else if ($scope.cal.range[0]) {
                var strString = $scope.cal.range[0].toISOString().split('T')[0];
                url += '&date_from__exact=' + strString;
            }

            $http({method:'GET', url:url })
                .success(function(data){
                    $scope.events = data.objects;
                }).error(function(data, status){
                    console.log("Opps we errored out on events.")
                });
        };



}]);