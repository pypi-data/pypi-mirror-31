(function (angular, undefined) {
  'use strict';
  
  /*
  module: congoApp.forms
  Provide solution to render ng-mesages form ajax and regular django form.
  */
  var saigonForms = angular.module('saigon.forms', []);
  
  function isField(field) {
    return (typeof field === 'object' && field.hasOwnProperty('$modelValue'));
  }
  
  saigonForms.factory('sgForm', function ($timeout) {
    var NON_FIELD_ERRORS = '__all__';
    var self = this;
    
    return {
      clearEmptyProps: function(obj) {
        $.each(obj, function (key, value) {
          if (obj.hasOwnProperty(key) && obj[key] === "") obj[key] = null;
        });
      },
      
      // set errors on form
      setErrors: function(form, errors) {
        if (angular.isArray(errors[NON_FIELD_ERRORS])) {
          form.$setValidity('rejected', false);
          form.$message = errors[NON_FIELD_ERRORS][0];
          form.$setDirty();
          
        } else {
          form.$setValidity('rejected', true);
          form.$message = "";
        }
        
        angular.forEach(form, function(field, key) {
          
          if (isField(field)) {
            if (angular.isArray(errors[key])) {
              
              field.$setValidity('rejected', false);
              field.$message = errors[key][0];
              $timeout(function() {
                // field.$setDirty(); // @FG nie jestem pewien po co to bylo
                field.$setTouched();
              })
              
              // hide rejected errors on keyup
              var fieldElement = $("input[name='" + key + "'], textarea[name='" + key + "']");
              if (!fieldElement.hasClass('sg-keyup')) {
                fieldElement.addClass('sg-keyup');
                fieldElement.keyup(function() {
                  $timeout(function() {
                    field.$setValidity('rejected', true);
                  })
                })
              }
                            
            } else {
              field.$setValidity('rejected', true);
              field.$message = "";
            }
            field.$validate();
          }
        });
        
      }
    }
    
  });
  
  // fill form by json data
  saigonForms.directive('sgDjForm', function(sgForm) {
    /*
     * Usage:
     * <form name="myForm2" action="." method="post" {% ng_form form=form %} novalidate>
     * 
     */
    
    return {
      restrict: 'A',
      require: '^form',
      scope: {
        sgDjForm: '@',
      },
     
      link: function (scope, element, attr, formCtrl) {
        scope.djForm = JSON.parse(scope.sgDjForm);
        
        scope.data = scope.djForm[0];
        scope.errors = scope.djForm[1];
        
        // set data values
        angular.forEach(formCtrl, function(field, key) {
          if (isField(field)) {
            var fieldElement = element.find('[name="' + field.$name  + '"]');
                        
            var fieldNgModel = fieldElement.attr('ng-model');
            var fieldType = fieldElement.attr('type');
            var fieldData = scope.data[field.$name];
            var fieldScope = angular.element(element).scope();
            
            // assign data to ng-model
            var splitted = fieldNgModel.split("."); 
             
            // jesli jest tylko jeden element, od razu przypisujemy go do scope
            if (splitted.length == 1) {
              
              if (fieldType == 'checkbox') {
                // jedyny sposob na ustawienie checkboxa
                fieldScope[fieldNgModel] = fieldData ? true : false;
              } else {
                fieldScope[fieldNgModel] = fieldData;
              }
              
            } else {
              
              // @FG trzeba to dopiescici, spokojnie mozna to zrobic w jednej petli bez tego if length...
              
              var _field = fieldScope;
              angular.forEach(splitted, function(obj) {
                _field = _field['' + obj + ''];
              })
              _field = fieldData; 
              
            }
            
          } 
        })

        // set errors
        if (scope.errors) {
          sgForm.setErrors(formCtrl, scope.errors);
        }
        
      }     
    }
    
  });
  
}(window.angular));