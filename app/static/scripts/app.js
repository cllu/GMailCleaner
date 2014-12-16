/*global angular*/

angular.module('app', ['ngRoute'])
  .config(['$routeProvider', '$locationProvider', function ($routeProvider, $locationProvider) {

    $routeProvider.

      when('/', {
        controller: 'IndexCtrl',
        templateUrl: '/static/templates/index.html'
      }).

      when('/app/', {
        controller: 'AppCtrl',
        templateUrl: '/static/templates/app.html'
      }).

      when('/auth/', {
        controller: 'AuthCtrl',
        template: ' '
      }).

      when('/auth/callback/', {
        controller: 'AuthCallbackCtrl',
        template: ' '
      }).

      otherwise({redirectTo: '/'});

    $locationProvider.html5Mode(true);
  }]);

angular.module('app')
  .controller('IndexCtrl', ['$scope', function ($scope) {

  }]);

angular.module('app')
  .controller('AuthCtrl', ['$scope', function ($scope) {
    // ask the backend API to redirect us
    location.href = '/api/auth/';
  }]);

angular.module('app')
  .controller('AuthCallbackCtrl', ['$scope', '$http', '$location', function ($scope, $http, $location) {
    //
    var params = $location.search();
    $http.get('/api/auth/callback/', {params: params})
      .success(function (data) {
        $location.search({});
        $location.path('/app/')
      })
      .error(function (data) {
        console.log(data);
      });

  }]);

angular.module('app')
  .controller('AppCtrl', ['$http', '$scope', 'FILTERS', function ($http, $scope, FILTERS) {

    $scope.inPreviewRequest = false;
    $scope.inPreview = false;

    $scope.filters = FILTERS;

    var getFilterString = function () {
      // find enabled filters
      var enabledFilterValues = [];
      angular.forEach($scope.filters, function (filter) {
        if (filter.enabled) {
          enabledFilterValues.push('(' + filter.value + ')');
        }
      });
      return enabledFilterValues.join(' OR ')
    };

    $scope.previewMessages = function () {

      var filterString = getFilterString();

      if (filterString.length === 0) {
        alert('no filters are selected');
        return;
      }

      var params = {
        with_details: true,
        max_results: 10,
        q: filterString
      };
      $scope.inPreview = false;
      $scope.inPreviewRequest = true;
      $http.get('/api/messages/', {params: params})
        .success(function (data) {

          // toggle state
          $scope.inPreview = true;
          $scope.inPreviewRequest = false;

          $scope.messages = data.messages;
          $scope.total = data.total;
        })
        .error(function (data) {
          console.log(data);

          $scope.inPreviewRequest = false;
          $scope.error = true;
          $scope.message = data.message;
        });
    };

    var deleteMessageWithIds = function (ids, successCallback, errorCallback) {
      var data = {
        ids: ids
      };
      $http.delete('/api/messages/', {data: data})
        .success(function (data) {
          successCallback(data.num_deleted);
        })
        .error(function (data) {
          console.log(data);
          errorCallback();
        });
    };

    $scope.deleteMessages = function () {
      var filterString = getFilterString();

      if (filterString.length === 0) {
        alert('no filters are selected');
        return;
      }
      var params = {
        with_details: false,
        q: filterString,
        max_results: 1000
      };

      $scope.inDelete = true;
      $scope.numMessagesToDelete = 0;
      $scope.numMessagesDeleted = 0;

      $http.get('/api/messages/', {params: params})
        .success(function (data) {
          console.log(data);

          $scope.numMessagesToDelete = data.total;
          $scope.numMessagesDeleted = 0;

          var messageIds = [];
          angular.forEach(data.messages, function (message) {
            messageIds.push(message.id);
          });

          console.log('num of messages to delete: ' + messageIds.length);
          console.log(messageIds);

          // split message ids into batches
          var i, j, chunk, chunkSize = 100;
          for (i = 0, j = messageIds.length; i < j; i += chunkSize) {
            chunk = messageIds.slice(i, i + chunkSize);
            // do whatever
            deleteMessageWithIds(chunk, function(numDeleted) {
              $scope.numMessagesDeleted += numDeleted;
            });
          }
        })
        .error(function (data) {
          console.log(data);
        });
    };

  }]);
