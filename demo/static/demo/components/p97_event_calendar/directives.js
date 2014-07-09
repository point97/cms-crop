angular.module('cropApp')
    .directive('eventcalendar', function(){


    function calCtrl($scope){
        $scope.cal = {}
        $scope.cal.active_date = '';

        $scope.today = function() {
            $scope.dt = new Date();
        };
        $scope.today();
        $scope.minDate = $scope.dt;
        $scope.cal.active_date = $scope.dt;

        // Get the first 5 events.
        $scope.events = [
            {
                date_from:'2014-07-17', 
                date_to:'2014-07-18', 
                title:'Title goes here', 
                short_description :'Short description goes here', 
                location:'It happens here', 
                body: "Body text goes here."
            },{
                date_from:'2014-07-19', 
                date_to:'2014-07-18', 
                title:'Title goes here 2', 
                short_description :'Short description goes here 2', 
                location:'It happens here 2', 
                body: "Body text goes here. 2"
            }
        ];

        
    }

    return {
        templateUrl: "/static/demo/components/p97_event_calendar/views/event_calendar.html",
        scope :{},
        controller:calCtrl
    };
}).directive('eventslist', function(){
    return {
        require: '^eventcalendar',
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