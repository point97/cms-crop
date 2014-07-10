angular.module('cropApp')
    .directive('eventCalendar', function($http){

    function calCtrl($scope, $http){
        $scope.cal = {}
        $scope.cal.active_date = '';

        $scope.today = function() {
            $scope.dt = new Date();
        };
        $scope.today();
        $scope.minDate = $scope.dt;
        $scope.cal.active_date = $scope.dt;

        // Get the first 5 events.
        $scope.events = [];

        $scope.get_events = function(date) {
            $http({method:'GET', url:'/api/v1/event/?format=json' })
                .success(function(data){
                    $scope.events = data.objects;
                }).error(function(data, status){
                    console.log("Opps we errored out on events.")
                });
        }
        
        $scope.get_events('');
    }

    return {
        templateUrl: "/static/demo/components/p97_event_calendar/views/event_calendar.html",
        scope :{},
        controller:calCtrl
    };
}).directive('eventsList', function(){
    /*
    Inputs:
        date - [String] ISO 8601 Date
        events - A list of event objects to display. Each event has keywords:
                title
                short_description
                url_path: A link to the event page.

    */
    return {
        require: '^eventCalendar',
        restrict: 'AE',
        transclude: true,
        scope: {
            date: "=",
            events: "="
        },
        link: function(scope, element, attrs) {
        },
        templateUrl: '/static/demo/components/p97_event_calendar/views/events_list.html'
    };
});