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
            $scope.topics.active = topic;
        };

        $scope.$on('slideChange', function(rs, index){
            var topic_slug = angular.element(".topic-menu-item").eq(index).attr("id");
            $scope.$apply(function () {
                // Without $apply() this changed variable doesn't trigger a $watch()
                // needed to keep the UI in sync.
                $scope.setTopic(topic_slug);
            });
        });

        $scope.get_events = function(date, offset_url) {

            var url = '/api/v1/event/?format=json&limit=5';
            if (typeof(offset_url) !== 'undefined') {
                url = offset_url;
            } else if ($scope.cal.range[0] && $scope.cal.range[1]) {
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
                    $scope.events.meta = data.meta;
                }).error(function(data, status){
                    console.log("Opps we errored out on events.")
                });
        };

        // nextBtnCallback
        $scope.nextBtnCallback = function () {
            $scope.get_events([], $scope.events.meta.next);  
        };

        // prevBtnCallback
        $scope.prevBtnCallback = function () {
            $scope.get_events([], $scope.events.meta.previous);  
        };

}]);