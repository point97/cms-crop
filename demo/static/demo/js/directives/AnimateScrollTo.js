/**
 * When added to a in-page link simple scrollTo directive . The directive also
 * catches the locationChangeStart event thus preventing a page reload.
 * From http://plnkr.co/edit/Sl2V4u3tVzsqEj7ttgNi?p=preview
 */
angular.module('cropApp')
  .directive('animateScrollTo', function () {
    return function(scope, element, attrs) {
        element.bind('click', function(event) {
            /* Prevent the standard click action */
            event.stopPropagation();
            // scope.$on('$locationChangeStart', function(ev) {
            //   ev.preventDefault();
            // });

            /* Animate scroll */
            var speed = 300;
            if (attrs.animateScrollTo !== '') {
                var hash = '#' + attrs.animateScrollTo;
                $('html,body').animate({scrollTop: $(hash).offset().top}, speed);
                window.location.hash = attrs.animateScrollTo;
            }
        });
    };
});