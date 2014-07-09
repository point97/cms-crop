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

}]).directive('carousel', function(){

    function link(scope, elt, attr){

        /* Initialise bxSlider */
        window.slider = $(elt.find(".bxslider")).bxSlider({
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
                scope.$emit('slideChange', newIndex)
            },
            onSlidePrev : function(slideElement, oldIndex, newIndex){
                scope.$emit('sdlideChange', newIndex)
            }
        });


        scope.$watch('topics.active', function(newValue){

            if (newValue){
                console.log("Active topic changed "+newValue);
                var index = _.indexOf(scope.topics.slugs, newValue);
                console.log("Changing to slide "+index);
                window.slider.goToSlide(index);
            }

        });
    };

    return {
        scope :{
            topics : "="
        },
        link:link,
    };
});