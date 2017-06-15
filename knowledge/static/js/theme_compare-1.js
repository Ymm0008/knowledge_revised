function getLocalTime(nS) {
    return new Date(parseInt(nS) * 1000).toLocaleString().replace(/年|月|\//g, "-").replace(/日|上午|下午/g, " ").substr(0,10);
}
require.config({
    paths: {
        echarts: '/static/js/echarts-2/build/dist',
    }
});
//包含事件
var flag='all';
function theme_include() {
    var theme_list_url='/theme/get_difference_event/?submit_user='+submit_user+'&theme_name1='+theme_1+
        '&theme_name2='+theme_2+'&flag='+flag;
    $.ajax({
        url:theme_list_url,
        type: 'GET',
        dataType: 'json',
        async: true,
        success:theme_list
    });
}
theme_include();
function theme_list(data) {
    var data = eval(data);
    var data1=data.detail_result1;
    var data2=data.detail_result2;
    var things1=[],things2=[];
    $.each(data1,function (index,item) {
        things1.push({
            'id':item[0],
            'event_name':item[1],
            'event_type':item[2],
            'date':item[3],
            'location':item[4],
            'people':item[5],
            'weibo':item[6],
            'keywords':item[7],
            'label':item[8],
        })
    });
    $.each(data2,function (index,item) {
        things2.push({
            'id':item[0],
            'event_name':item[1],
            'event_type':item[2],
            'date':item[3],
            'location':item[4],
            'people':item[5],
            'weibo':item[6],
        })
    });
    $('#list-1').bootstrapTable('load', things1);
    $('#list-1').bootstrapTable({
        data:things1,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 3,//单页记录数
        // pageList: [10, 20, 40, 80],//分页步进值
        sidePagination: "client",//服务端分页
        searchAlign: "left",
        searchOnEnterKey: false,//回车搜索
        showRefresh: false,//刷新按钮
        showColumns: false,//列选择按钮
        buttonsAlign: "right",//按钮对齐方式
        locale: "zh-CN",//中文支持
        detailView: false,
        showToggle:false,
        sortName:'bci',
        sortOrder:"desc",
        columns: [
            {
                title: "事件名称",//标题
                field: "event_name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                // formatter: function (value, row, index) {
                //     return row[1];
                // }
            },
            {
                title: "事件类型",//标题
                field: "event_type",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.event_type==''||row.event_type=='null'||row.event_type=='unknown'){
                        return '未知';
                    }else {
                        return row.event_type;
                    }
                }
            },
            {
                title: "发生时间",//标题
                field: "date",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.date==''||row.date=='NULL'){
                        return '暂无数据';
                    }else {
                        return getLocalTime(row.date);
                    }
                },
            },
            {
                title: "发生地点",//标题
                field: "location",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.location==''||row.location=='NULL'){
                        return '未知';
                    }else {
                        return row.location;
                    }
                },
            },
            {
                title: "参与人数",//标题
                field: "people",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.people==''||row.people=='NULL'){
                        return '暂无';
                    }else {
                        return row.people;
                    }
                },
            },
            {
                title: "微博数量",//标题
                field: "weibo",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.weibo==''||row.weibo=='NULL'){
                        return '暂无';
                    }else {
                        return row.weibo;
                    }
                },
            },

        ],
        onClickCell: function (field, value, row, $element) {
            if ($element[0].cellIndex==0){
                window.open('/index/event/?user_id='+row.id);
            }
        },
    });
    $('#list-2').bootstrapTable('load', things2);
    $('#list-2').bootstrapTable({
        data:things2,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 3,//单页记录数
        // pageList: [10, 20, 40, 80],//分页步进值
        sidePagination: "client",//服务端分页
        searchAlign: "left",
        searchOnEnterKey: false,//回车搜索
        showRefresh: false,//刷新按钮
        showColumns: false,//列选择按钮
        buttonsAlign: "right",//按钮对齐方式
        locale: "zh-CN",//中文支持
        detailView: false,
        showToggle:false,
        sortName:'bci',
        sortOrder:"desc",
        columns:  [
            {
                title: "事件名称",//标题
                field: "event_name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                // formatter: function (value, row, index) {
                //     return row[1];
                // }
            },
            {
                title: "事件类型",//标题
                field: "event_type",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.event_type==''||row.event_type=='null'||row.event_type=='unknown'){
                        return '未知';
                    }else {
                        return row.event_type;
                    }
                }
            },
            {
                title: "发生时间",//标题
                field: "date",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.date==''||row.date=='NULL'){
                        return '暂无数据';
                    }else {
                        return getLocalTime(row.date);
                    }
                },
            },
            {
                title: "发生地点",//标题
                field: "location",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.location==''||row.location=='NULL'){
                        return '未知';
                    }else {
                        return row.location;
                    }
                },
            },
            {
                title: "参与人数",//标题
                field: "people",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.people==''||row.people=='NULL'){
                        return '暂无';
                    }else {
                        return row.people;
                    }
                },
            },
            {
                title: "微博数量",//标题
                field: "weibo",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.weibo==''||row.weibo=='NULL'){
                        return '暂无';
                    }else {
                        return row.weibo;
                    }
                },
            },

        ],
        onClickCell: function (field, value, row, $element) {
            if ($element[0].cellIndex==0){
                window.open('/index/event/?user_id='+row.id);
            }
        },
    });
};
$('#container .include .edit input').on('click',function () {
    if ($(this).val()=='all'){
        flag='all';
        theme_include();
    }else if ($(this).val()=='diff'){
        flag='diff';
        theme_include();
    }else{
        flag='same';
        theme_include();
    }
});

//包含人物
var user_flag='all';
function user_include() {
    var user_list_url='/theme/get_difference_user/?submit_user='+submit_user+'&theme_name1='+theme_1+
        '&theme_name2='+theme_2+'&flag='+user_flag;
    $.ajax({
        url:user_list_url,
        type: 'GET',
        dataType: 'json',
        async: true,
        success:user_list
    });
}
user_include();
function user_list(data) {
    var data = eval(data);
    var data1=data.detail_result1;
    var data2=data.detail_result2;
    var things1=[],things2=[];
    $.each(data1,function (index,item) {
        things1.push({
            'id':item[0],
            'name':item[1],
            'location':item[2],
            'influ':item[3],
            'active':item[4],
            'sensitive':item[5],
        })
    });
    $.each(data2,function (index,item) {
        things2.push({
            'id':item[0],
            'name':item[1],
            'location':item[2],
            'influ':item[3],
            'active':item[4],
            'sensitive':item[5],
        })
    });
    $('#list-1-user').bootstrapTable('load', things1);
    $('#list-1-user').bootstrapTable({
        data:things1,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 3,//单页记录数
        // pageList: [10, 20, 40, 80],//分页步进值
        sidePagination: "client",//服务端分页
        searchAlign: "left",
        searchOnEnterKey: false,//回车搜索
        showRefresh: false,//刷新按钮
        showColumns: false,//列选择按钮
        buttonsAlign: "right",//按钮对齐方式
        locale: "zh-CN",//中文支持
        detailView: false,
        showToggle:false,
        sortName:'bci',
        sortOrder:"desc",
        columns: [
            {
                title: "用户ID",//标题
                field: "id",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                // formatter: function (value, row, index) {
                //     return row[0];
                // }
            },
            {
                title: "昵称",//标题
                field: "name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.name==''||row.name=='unknown'||row.name=='NULL'){
                        return row.id;
                    }else {
                        return row.name;
                    }
                }
            },
            {
                title: "注册地",//标题
                field: "location",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.location==''||row.location=='null'||row.location=='unknown'){
                        return '未知';
                    }else {
                        return row.location;
                    }
                },
            },
            {
                title: "影响力",//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.influ==''||row.influ=='NULL'||row.influ=='unknown'){
                        return '未知';
                    }else {
                        return row.influ.toFixed(2);
                    }
                },
            },
            {
                title: "活跃度",//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.active==''||row.active=='NULL'||row.active=='unknown'){
                        return '暂无';
                    }else {
                        return row.active.toFixed(2);
                    }
                },
            },
            {
                title: "敏感度",//标题
                field: "sensitive",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.sensitive==''||row.sensitive=='NULL'||row.sensitive=='unknown'){
                        return '暂无';
                    }else {
                        return row.sensitive.toFixed(2);
                    }
                },
            },

        ],
        onClickCell: function (field, value, row, $element) {
            if ($element[0].cellIndex==0){
                window.open('/index/person/?user_id='+row.id);
            }
        },
    });
    $('#list-2-user').bootstrapTable('load', things2);
    $('#list-2-user').bootstrapTable({
        data:things2,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 3,//单页记录数
        // pageList: [10, 20, 40, 80],//分页步进值
        sidePagination: "client",//服务端分页
        searchAlign: "left",
        searchOnEnterKey: false,//回车搜索
        showRefresh: false,//刷新按钮
        showColumns: false,//列选择按钮
        buttonsAlign: "right",//按钮对齐方式
        locale: "zh-CN",//中文支持
        detailView: false,
        showToggle:false,
        sortName:'bci',
        sortOrder:"desc",
        columns: [
            {
                title: "用户ID",//标题
                field: "id",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                // formatter: function (value, row, index) {
                //     return row[0];
                // }
            },
            {
                title: "昵称",//标题
                field: "name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.name==''||row.name=='unknown'||row.name=='NULL'){
                        return row.id;
                    }else {
                        return row.name;
                    }
                }
            },
            {
                title: "注册地",//标题
                field: "location",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.location==''||row.location=='null'||row.location=='unknown'){
                        return '未知';
                    }else {
                        return row.location;
                    }
                },
            },
            {
                title: "影响力",//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.influ==''||row.influ=='NULL'||row.influ=='unknown'){
                        return '未知';
                    }else {
                        return row.influ.toFixed(2);
                    }
                },
            },
            {
                title: "活跃度",//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.active==''||row.active=='NULL'||row.active=='unknown'){
                        return '暂无';
                    }else {
                        return row.active.toFixed(2);
                    }
                },
            },
            {
                title: "敏感度",//标题
                field: "sensitive",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.sensitive==''||row.sensitive=='NULL'||row.sensitive=='unknown'){
                        return '暂无';
                    }else {
                        return row.sensitive.toFixed(2);
                    }
                },
            },
        ],
        onClickCell: function (field, value, row, $element) {
            if ($element[0].cellIndex==0){
                window.open('/index/person/?user_id='+row.id);
            }
        },
    });
};
$('#container .link_user .edit-user input').on('click',function () {
    if ($(this).val()=='all'){
        user_flag='all';
        user_include();
    }else if ($(this).val()=='diff'){
        user_flag='diff';
        user_include();
    }else{
        user_flag='same';
        user_include();
    }
});

//自动标签（关键词）
var keywords_flag='all';
function keywords() {
    var keywords_include_url='/theme/get_difference_keywords/?submit_user='+submit_user+'&theme_name1='+theme_1+
        '&theme_name2='+theme_2+'&flag='+keywords_flag;
    $.ajax({
        url:keywords_include_url,
        type: 'GET',
        dataType: 'json',
        async: true,
        success:keywords_include
    });
}
keywords();
function createRandomItemStyle() {
    return {
        normal: {
            color: 'rgb(' + [
                Math.round(Math.random() * 160),
                Math.round(Math.random() * 160),
                Math.round(Math.random() * 160)
            ].join(',') + ')'
        }
    };
}
function keywords_include(data) {
    var data = eval(data);
    var data1=data[0];
    var data2=data[1];
    var series_1=[],series_2=[];
    for (var a=0;a<data1.length;a++){
        if (data1[a] !=''){
            series_1.push(
                {
                    name: data1[a],
                    value: 30,
                    itemStyle: createRandomItemStyle()
                }
            );
        }

    };
    for (var b=0;b<data2.length;b++){
        if (data2[b]!=''){
            series_2.push(
                {
                    name: data2[b],
                    value: 30,
                    itemStyle: createRandomItemStyle()
                }
            );
        }
    };

    if(series_1.length==0){
        $('#list-1-words').html('暂无数据').css({'lineHeight':'300px','textAlign':'center'});;
    }else {
        require(
            [
                'echarts',
                'echarts/chart/wordCloud'
            ],
            function (ec) {
                // 基于准备好的dom，初始化echarts图表
                var myChart = ec.init(document.getElementById('list-1-words'));

                option = {
                    title: {
                        text: '',
                    },
                    tooltip: {
                        show: true
                    },
                    series: [{
                        // name: 'Google Trends',
                        type: 'wordCloud',
                        size: ['80%', '80%'],
                        textRotation : [0, 0, 0, 0],
                        textPadding: 0,
                        autoSize: {
                            enable: true,
                            minSize: 14
                        },
                        data:series_1,
                    }]
                };
                myChart.setOption(option);
                // var ecConfig = require('echarts/config');
                // myChart.on(ecConfig.EVENT.HOVER, function (param){
                //     var selected = param.name;
                // });

            }
        );
    };

    if(series_2.length==0){
        $('#list-2-words').html('暂无数据').css({'lineHeight':'300px','textAlign':'center'});;
    }else {
        require(
            [
                'echarts',
                'echarts/chart/wordCloud'
            ],
            function (ec) {
                var myChart = ec.init(document.getElementById('list-2-words'));

                option = {
                    title: {
                        text: '',
                    },
                    tooltip: {
                        show: true
                    },
                    series: [{
                        // name: 'Google Trends',
                        type: 'wordCloud',
                        size: ['80%', '80%'],
                        textRotation : [0, 0, 0, 0],
                        textPadding: 0,
                        autoSize: {
                            enable: true,
                            minSize: 14
                        },
                        data:series_2,
                    }]
                };
                myChart.setOption(option);
            }
        );
    }



};
$('#container .key_words .edit-words input').on('click',function () {
    if ($(this).val()=='all'){
        keywords_flag='all';
        keywords();
    }else if ($(this).val()=='diff'){
        keywords_flag='diff';
        keywords();
    }else{
        keywords_flag='same';
        keywords();
    }
})

//标签
var tag_flag='all';
function label_tag() {
    var tag_url='/theme/get_difference_k_label/?submit_user='+submit_user+'&theme_name1='+theme_1+
        '&theme_name2='+theme_2+'&flag='+tag_flag;
    $.ajax({
        url:tag_url,
        type: 'GET',
        dataType: 'json',
        async: true,
        success:tag
    });
}
label_tag();

function tag(data) {
    var data = eval(data);
    var data1=data[0];
    var data2=data[1];
    var series_1=[],series_2=[];
    for (var a=0;a<data1.length;a++){
        if (data1[a]!=''){
            series_1.push(
                {
                    name: data1[a],
                    value: 30,
                    itemStyle: createRandomItemStyle()
                }
            );
        }

    };
    for (var b=0;b<data2.length;b++){
        if(data2[b]!=''){
            series_2.push(
                {
                    name: data2[b],
                    value: 30,
                    itemStyle: createRandomItemStyle()
                }
            );
        }

    };

    if (series_1.length==0){
        $('#list-1-tags').html('暂无数据').css({'lineHeight':'300px','textAlign':'center'});
    }else {
        require(
            [
                'echarts',
                'echarts/chart/wordCloud'
            ],
            function (ec) {
                // 基于准备好的dom，初始化echarts图表
                var myChart = ec.init(document.getElementById('list-1-tags'));

                option = {
                    title: {
                        text: '',
                    },
                    tooltip: {
                        show: true
                    },
                    series: [{
                        // name: 'Google Trends',
                        type: 'wordCloud',
                        size: ['80%', '80%'],
                        textRotation : [0, 0, 0, 0],
                        textPadding: 0,
                        autoSize: {
                            enable: true,
                            minSize: 14
                        },
                        data:series_1,
                    }]
                };
                myChart.setOption(option);
                // var ecConfig = require('echarts/config');
                // myChart.on(ecConfig.EVENT.HOVER, function (param){
                //     var selected = param.name;
                // });
            }
        );
    }

    if (series_2.length==0){
        $('#list-2-tags').html('暂无数据').css({'lineHeight':'300px','textAlign':'center'});
    }else {
        require(
            [
                'echarts',
                'echarts/chart/wordCloud'
            ],
            function (ec) {

                var myChart = ec.init(document.getElementById('list-2-tags'));

                option = {
                    title: {
                        text: '',
                    },
                    tooltip: {
                        show: true
                    },
                    series: [{
                        // name: 'Google Trends',
                        type: 'wordCloud',
                        size: ['80%', '80%'],
                        textRotation : [0, 0, 0, 0],
                        textPadding: 0,
                        autoSize: {
                            enable: true,
                            minSize: 14
                        },
                        data:series_2,
                    }]
                };
                myChart.setOption(option);
            }
        );
    }



};
$('#container .tags .edit-tags input').on('click',function () {
    if ($(this).val()=='all'){
        tag_flag='all';
        label_tag();
    }else if ($(this).val()=='diff'){
        tag_flag='diff';
        label_tag();
    }else{
        tag_flag='same';
        label_tag();
    }
})