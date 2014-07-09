angular.module('cropApp')
    .directive('exploreCarousel', function(){

    function link(scope, elt, attr){

        /* Initialise bxSlider */
        window.slider = $(".explore-carousel .bxslider").bxSlider({
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