/*
    This requires Date.js

    To use, add a method get_events to the parent controller. This
    method should take an array that has start and end, DateJS objects. 
    
    It should return list of events - A list of event objects to display. 
    Each event has keywords:
        title
        short_description
        body
        url_path: A link to the event page.
    
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

        
        $scope.get_events('');

        // Add watcher for month change and update cal.range to the slected month
        $scope.$watch(function(){
            return $('thead tr:nth-child(1) th:nth-child(2) strong').text();
        }, function(newValue){
            // Calendar Month change
            if (newValue) {
                startDate = Date.parse(newValue);
                endDate = Date.parse(newValue).moveToLastDayOfMonth();
                $scope.cal.range = [startDate,endDate];
                $scope.get_events();
            }
            
        });

        // A watcher for user selected date, dt. Updates cal.range to a one date query.
        $scope.$watch('dt', function(newValue){
            if (newValue){
                date = Date.parse(newValue);
                $scope.cal.range = [newValue, null];
                $scope.get_events();
            }
            
        });

    }

    return {
        templateUrl: "/static/demo/components/p97_event_calendar/views/event_calendar.html",
        //scope :{},
        controller:calCtrl
    };
}).directive('eventsList', function(){
    /*
    Inputs:
        date - [String] ISO 8601 Date
        events - A list of event objects to display. Each event has keywords:
                title
                short_description
                body
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