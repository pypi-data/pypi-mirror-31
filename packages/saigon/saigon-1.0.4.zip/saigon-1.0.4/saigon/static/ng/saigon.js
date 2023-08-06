var app = angular.module('saigon', []);

app.factory('saigonCommon', function($window, $rootScope) {
  var factory = {};
    
  /* Pozwala na zmiane url'a. */
  factory.goTo = function(url) {
    $window.open(url, '_self');
  }
  
  /* Zwraca aktualny rozmiar ekranu */
  factory.device = function(scope) {
   /*
   * W przypadku korzystania z device w zagniezdzonych scope'ach np. w dialogu
   * Istnieje mozliwosc przekazania scope do ktorego maja byc zapisane stale device.
   * W przeciwnym razie zostana zapisane do $rootScope
   */ 
    scope = scope ? scope : $rootScope;
    
    var SM = 576;
    var MD = 768;
    var LG = 992;
    var XL = 1200;
     
    var dd = {
      xl_e: false,
      xl_lt: false,

      lg_e: false,
      lg_lt: false,
      lg_gte: false,
      lg_lt: false,
      lg_lte: false,
        
      md_e: false,
      md_gt: false,
      md_gte: false,
      md_lt: false,
      md_lte: false,
  
      sm_e: false,
      sm_gt: false,
      sm_gte: false,
      sm_lt: false,
      sm_lte: false,
                 
      xs_e: false,
      xs_gt: false,
    }
      
    var getDevice = function() {
      // czyscimy stare zmiany, ustawiamy na false
      angular.forEach(dd, function(value, key) {
        dd[key] = false;
      })      
      
      // pobieramy size
      var size = $window.innerWidth;
          
      // xl
      if (size >= XL) dd.xl_e = true; 
      if (size < XL) dd.xl_lt = true;
          
      // lg
      if (size < XL && size >= LG) dd.lg_e = true;
      if (size >= XL) dd.lg_gt = true;
      if (size >= LG) dd.lg_gte = true;
      if (size < LG) dd.lg_lt = true;
      if (size < XL) dd.lg_lte = true;

      // md
      if (size < LG && size >= MD) dd.md_e = true;
      if (size >= LG) dd.md_gt = true;
      if (size >= MD) dd.md_gte = true;
      if (size < MD) dd.md_lt = true;
      if (size < LG) dd.md_lte = true;
          
      // sm
      if (size < MD && size >= SM) dd.sm_e = true;
      if (size >= MD) dd.sm_gt = true;
      if (size >= SM) dd.sm_gte = true;
      if (size < SM) dd.sm_lt = true;
      if (size < MD) dd.sm_lte = true;
          
      // xs
      if (size < SM) dd.xs_e = true;
      if (size >= SM) dd.xs_gt = true;
          
      // zapisujemy w rootScope zmienne
      angular.forEach(dd, function(value, key) {
        scope[key] = value;
      })
    }
    
    // first time
    getDevice();

    // resize
    angular.element($window).bind('resize', function(){
      getDevice();
      scope.$digest();
    });
    
    return dd;
  }
    
  return factory;
});

app.directive('keepParameters', function($location, $timeout){
  /*
   * Keep search parameters from url.
   * 
   */
  
  return {

    link: function(scope, element, attrs) {
      $timeout(function() {
        
        var url = element.attr('href');
        var parameters = (url.includes('?')) ? "&" : "?";
        var idx = 0;
        
        angular.forEach($location.search(), function(value, key) {
          var divider = (idx > 0) ? '&' : '';
          parameters += divider + key + "=" + value;
          idx++;
        })
        
        // set parameters
        url += parameters;
        element.attr('href', url);
        
      })
      
    }
    
  }
})

app.directive('compileHtml', function ($compile, $parse) {
  /*
   * js:
   * $scope.myvar = $sce.trustAsHtml("<span style='color:red'>yolo!</span>"); 
   *  
   * html:
   * <div compile-html ng-bind-html="myVar"></div> 
   */
 
    return {
        restrict: 'A',
        link: function ($scope, element, attr) {
            var parse = $parse(attr.ngBindHtml);

            function value() {
                return (parse($scope) || '').toString();
            }

            $scope.$watch(value, function () {
                $compile(element, null, -9999)($scope);
            });
        }
    }
});