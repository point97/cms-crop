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


/**
 * Replace all SVG images with inline SVG allowing us to change the color, size, etc
 * with css like so:
 *
 * #img-tag-id:hover path {
 *   fill: red;
 * }
 *
 * OR
 *
 * .img-tag-class:hover path {
 *   fill: red;
 * }
 *
 * http://stackoverflow.com/questions/11978995/how-to-change-color-of-svg-image-using-css-jquery-svg-image-replacement
 *
 */
$(document).ready(function () {
    jQuery('img.svg').each(function(){
        var $img = jQuery(this);
        var imgID = $img.attr('id');
        var imgClass = $img.attr('class');
        var imgURL = $img.attr('src');

        jQuery.get(imgURL, function(data) {
            // Get the SVG tag, ignore the rest
            var $svg = jQuery(data).find('svg');

            // Add replaced image's ID to the new SVG
            if(typeof imgID !== 'undefined') {
                $svg = $svg.attr('id', imgID);
            }
            // Add replaced image's classes to the new SVG
            if(typeof imgClass !== 'undefined') {
                $svg = $svg.attr('class', imgClass+' replaced-svg');
            }

            // Remove any invalid XML tags as per http://validator.w3.org
            $svg = $svg.removeAttr('xmlns:a');

            // Replace image with new SVG
            $img.replaceWith($svg);
        });

    });
});
