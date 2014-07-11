angular.module('cropApp')
    .directive('exploreCarousel', function(){

    function link(scope, elt, attr){

        /* Initialise bxSlider */
        window.slider = $(".explore-carousel .bxslider").bxSlider({
            captions: false,
            captions: false,
            nextText: '<i class="fa fa-angle-right"></i>',
            prevText: '<i class="fa fa-angle-left"></i>',

            onSlideNext: function(slideElement, oldIndex, newIndex){
                scope.$emit('slideChange', newIndex)
            },

            onSlidePrev: function(slideElement, oldIndex, newIndex){
                scope.$emit('slideChange', newIndex)
            }
        });

        /* Keep slider in sync with sidebar. */
        scope.$watch('topics.active', function(newValue){
            if (newValue){
                var index = _.indexOf(scope.topics.slugs, newValue);
                window.slider.goToSlide(index);
            }
        });
    };

    return {
        scope :{
            topics : "=",
            test: '='
        },
        link:link,
    };
});