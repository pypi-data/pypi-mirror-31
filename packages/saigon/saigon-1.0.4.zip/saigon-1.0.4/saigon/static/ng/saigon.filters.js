var app = angular.module('saigon');

app.filter("safe", function($sce) {
  /*
   *  Display html.
   *  
   *  Usage:
   *  <span ng-bind-html="color.get_stock_display|safe"></span>
   */
  
  return function(htmlCode){
    return $sce.trustAsHtml(htmlCode);
  }
});

app.filter('contains', function() {
  /*
   *  Return true if array contains needle.
   *  
   *  Usage:
   *  <span ng-if="myList|contains:'my_name'"></span>
   */
  return function (array, needle) {
    return array.indexOf(needle) >= 0;
  };
});

app.filter('orBlank', function() {
  /*
   *  Return (Brak) or custom label if not value 
   *  
   *  Usage:
   *  <span>[[ description|orBlank:'(Pusty)' ]]</span>
   */
  return function (value, label) {
    if (!value) {
      // obsluzyc brak gettext
      if (!label) label = "(" + gettext("Brak") + ")"; 
      return label;      
    } else {
      return value;
    }
  };
});