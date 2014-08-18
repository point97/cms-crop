angular.module('cropApp')
    .directive('switchLang', function($http){
        
        return {
            replace: true,  // Use the exuisting HTML which has the Django CSRF token.
            link : function(scope, element, attrs){
                if (location.pathname.search('^/es/') >= 0 ) {
                    scope.lang = 'es';
                }  else {
                    scope.lang = 'en';
                }
            },
        };
    }
);