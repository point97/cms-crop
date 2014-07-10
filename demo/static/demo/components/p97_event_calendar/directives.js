/*
    This requires Date.js
*/

angular.module('cropApp')
    .directive('eventCalendar', function($http){

    function calCtrl($scope, $http){
        $scope.cal = {}
        $scope.cal.active_date = '';
        
        // This is the range used to build the API queryy string.
        // Leave second entry null for single day queries
        $scope.cal.range = [null,null]; 

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

        // Add watcher for month change and update cal.range to the slected month
        $scope.$watch(function(){
            return $("thead tr:nth-child(1) th:nth-child(2) strong").text();
        }, function(newValue){
            // Calendar Month change
            startDate = Date.parse(newValue);
            endDate = Date.parse(newValue).moveToLastDayOfMonth();
            $scope.cal.range = [startDate,endDate];
        });

        // A watcher for user selected date, dt. Updates cal.range to a one date query.
        $scope.$watch('dt', function(newValue){
            date = Date.parse(newValue);
            $scope.cal.range = [newValue, null];
        });

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
        // scope: {
        //     date: "=",
        //     events: "="
        // },
        link: function(scope, element, attrs, calCtrl) {
        },
        templateUrl: '/static/demo/components/p97_event_calendar/views/events_list.html'
    };
});