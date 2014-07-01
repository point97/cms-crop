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
}]).directive('carousel', function(){
    
    function link(scope, elt, attr){
        
        /* Initialise bxSlider */
        $(elt.find(".bxslider")).bxSlider({
            captions: true,
            onSliderLoad: function(){
                console.log("Slider loaded");
                scope.nextBtn = elt.find(".bx-next");
                scope.prevBtn = elt.find(".bx-prev");
                
                scope.nextBtn.bind('click', function(e){
                    console.log('hello from', scope.nextBtn);
                });

                scope.prevBtn.bind('click', function(e){
                    console.log('hello from', scope.prevBtn); 
                });
            },
            onSlideNext : function(slideElement, oldIndex, newIndex){
                console.log(slideElement);
                console.log(oldIndex);
                console.log(newIndex);
            }
        });    
    };

    return {
        
        link:link
    };
});