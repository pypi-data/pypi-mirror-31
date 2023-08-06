(function (angular, undefined) {
  'use strict';
  
  /*
  module: saigon.urls
  Provide url reverse resolution functionality for django urls in angular
  Based on: https://github.com/jrief/django-angular/blob/master/djng/static/djng/js/django-angular.js
  Usage: djUrl.reverse(url_name, args_or_kwargs)

  Examples:
  - sgUrl.reverse('home', [user_id: 2]);
  - sgUrl.reverse('home', [2]);
   */
  var saigonUrls = angular.module('saigon.urls', []);
  
  saigonUrls.provider('sgUrl', function djUrlProvider() {
    var reverseUrl = '/reverse/';
    this.setReverseUrl = function (url) {
      reverseUrl = url;
    };
    this.$get = function () {
      return new djUrl(reverseUrl);
    };
  });
  
  /*
  url-reversing service
  */
  var djUrl = function (reverseUrl) {
    
    //Functions from angular.js source, not public available
    //See: https://github.com/angular/angular.js/issues/7429
    function forEachSorted(obj, iterator, context) {
      var keys = sortedKeys(obj);
      for (var i = 0; i < keys.length; i++) {
        iterator.call(context, obj[keys[i]], keys[i]);
      }
      return keys;
    }
    
    function sortedKeys(obj) {
      var keys = [];
      
      // ie not compatible
      // for (var key in obj) {
        // if (obj.hasOwnProperty(key)) {
          // keys.push(key);
        // }
      // }
      
      $.each(obj, function (key, value) {
        if (obj.hasOwnProperty(key)) {
          keys.push(key);
        }
      });
      
      return keys.sort();
    }
    
    function buildUrl(url, params) {
      if (!params) return url;
      var parts = [];
      
      forEachSorted(params, function (value, key) {
        if (value === null || value === undefined) return;
        if (angular.isObject(value)) {
          value = angular.toJson(value);
        }
        
        /*
        If value is a string and starts with ':' we don't encode the value to enable parametrized urls
        E.g. with .reverse('article',{id: ':id'} we build a url
        /angular/reverse/?dj_url_name=article?id=:id, which angular resource can use
        https://docs.angularjs.org/api/ngResource/service/$resource
        */
        if ((typeof value === 'string' || value instanceof String) && value.lastIndexOf(':', 0) === 0) {
          parts.push(encodeURIComponent(key) + '=' + value);
        } else {
          parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
        }
      });
      
      return url + (url.indexOf('?') === -1 ? '?' : '&') + parts.join('&');
    }
    
    // Service public interface
    this.reverse = function (url_name, args_or_kwargs) {
      
      var url = buildUrl(reverseUrl, { dj_url: url_name });
      
      /*
      Django wants arrays in query params encoded the following way: a = [1,2,3] -> ?a=1&a=2$a=3
      buildUrl function doesn't natively understand lists in params, so in case of a argument array
      it's called iteratively, adding a single parameter with each call
      
      url = buildUrl(url, {a:1}) -> returns /url?a=1
      url = buildUrl(url, {a:2}) -> returns /url?a=1&a=2
      ...
      */
             
      if (Array.isArray(args_or_kwargs)) {
        forEachSorted(args_or_kwargs, function (value) {
          url = buildUrl(url, { 'dj_args': value });
        });
        return url;
      }
      
      /*
      If there's a object of keyword arguments, a 'dj_url_kwarg_' prefix is prepended to each member
      Then we can directly call the buildUrl function
      */
      var params = {};
      forEachSorted(args_or_kwargs, function (value, key) {
        params['dj_kwarg_' + key] = value;
      });
      
      /*
      If params is empty (no kwargs passed) return url immediately
      Calling buildUrl with empty params object adds & or ? at the end of query string
      E.g. buldUrl('/url/dj_url_name=home', {}) -> /url/dj_url_name=home&
      */
      if (angular.equals(params, {})) {
        // If params is empty, no kwargs passed.
        return url;
      }
      
      return buildUrl(url, params);
    };
  };
}(window.angular));
