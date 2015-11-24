'use strict';

/**
 * @ngdoc service
 * @name angularGanttDemoApp.Sample
 * @description
 * # Sample
 * Service in the angularGanttDemoApp.
 */
angular.module('angularGanttDemoApp')
    .service('Sample', function Sample() {
        return {
            getSampleData: function() {
                return [
                        {name: '0001', children: ['0002', '0003', '0004', '0005'], content: '<a href="/issues/1">测试</a>'},
                        {name: '0002', content: '测试1', tasks: [
                            {color: '#F1C232', from: new Date(2015,9,15,0,0,0), to: new Date(2015,9,18,24,0,0), _from: '9.15', _to: '9.18', _status:'新建', _assignee: 'Eric', progress: 100}
                        ]},
                        {name: '0003', content: '测试2', tasks: [
                            {color: '#F1C232', from: new Date(2015,9,19,0,0,0), to: new Date(2015,9,20,24,0,0), _from: '9.15', _to: '9.18', _status:'新建', _assignee: 'Eric', progress: 0}
                        ]},
                        {name: '0004', content: '测试3', tasks: [
                            {color: '#F1C232', from: new Date(2015,9,22,0,0,0), to: new Date(2015,9,30,24,0,0), _from: '9.15', _to: '9.18', _status:'新建', _assignee: 'Eric', progress: 10}
                        ]},
                        {name: '0005', content: '测试4', tasks: [
                            {color: '#F1C232', from: new Date(2015,9,28,0,0,0), to: new Date(2015,10,5,24,0,0), _from: '9.15', _to: '9.18', _status:'新建', _assignee: 'Eric', progress: 75}
                        ]},

                        {name: '0006', children: ['0007'], content: '研发'},
                        {name: '0007', children: ['0008'], content: '研发1'},
                        {name: '0008', children: ['0009'], content: '研发1-1'},
                        {name: '0009', content: '研发1-1-1', tasks: [
                            {color: '#F1C232', from: new Date(2015,9,22,0,0,0), to: new Date(2015,9,30,24,0,0), _from: '9.15', _to: '9.18', _status:'新建', progress: 10}
                        ]},

                        {name: 'Development', content: '<i class="fa fa-file-code-o" ng-click="scope.handleRowIconClick(row.model)"></i> {{row.model.name}}'},
                    ];
            },
        };
    })
;
