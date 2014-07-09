$(document).ready(function(){
    /* Initialise bxSlider */
    $('.not-explore-carousel .bxslider').bxSlider({
        captions: true
    });
});

$(document).ready(function(){
    //Apply img-thumbnail class to body-content images
    $('.body-content img').addClass("img-thumbnail");
});


/**
 * Animate scrolling to mid-page anchors on initial load.
 */
$(document).ready(function () {
    var hash = window.location.hash,
        speed = 300;
    if (hash !== '') {
      //$('html,body').animate({scrollTop: $(hash).offset().top}, speed);
    }
});