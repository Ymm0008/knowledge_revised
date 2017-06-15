//包含人物
var include_user_url='/group/group_detail/?g_name='+group_name+'&submit_user='+submit_user;
$.ajax({
    url: include_user_url,
    type: 'GET',
    dataType: 'json',
    async: true,
    success:include_user
});
function include_user(data) {
    var data = eval(data);
    var peoples=[];
    $.each(data,function (index,item) {
        peoples.push({
            'id':item[0],
            'name':item[1],
            'location':item[2],
            'influence':item[3],
            'active':item[4],
            'sensitive':item[5],
            'keywords':item[6],
            'label':item[7],
            'type':item[8],
        })
    });
    $('#person').bootstrapTable('load', peoples);
    $('#person').bootstrapTable({
        data:peoples,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 5,//单页记录数
        pageList: [5, 20],//分页步进值
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
                formatter: function (value, row, index) {
                    return row.id;
                    if (row.name==''||row.name=='NULL'||row.name=='unknown'){
                        include_user_list.push('<span>'+row.id+'</span>');
                    }else {
                        include_user_list.push(row.name+'('+'<span>'+row.id+'</span>'+')');
                    }
                }
            },
            {
                title: "昵称",//标题
                field: "name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.name==''||row.name=='NULL'||row.name=='unknown'){
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
                    if (row.location==''||row.location=='NULL'||row.location=='unknown'){
                        return '未知';
                    }else {
                        return row.location;
                    }
                },
            },
            {
                title: "影响力",//标题
                field: "influence",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.influence==''||row.influence=='NULL'||row.influence=='unknown'){
                        return 0;
                    }else {
                        return row.influence.toFixed(2);
                    }
                },
            },
            {
                title: "活跃度",//标题
                field: "active",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.active==''||row.active=='NULL'||row.active=='unknown'){
                        return 0;
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
                        return 0;
                    }else {
                        return row.sensitive.toFixed(2);
                    }
                },
            },
            {
                title: "自动标签",//标题
                field: "keywords",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.keywords=='unknown'||row.keywords==''){
                        return '暂无';
                    }else {
                        return row.keywords.toString().split('&').slice(0,5);
                    }
                },
            },
            {
                title: "业务标签",//标题
                field: "label",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.label=='unknown'||row.label==''){
                        return '暂无';
                    }else {
                        return row.label.toString().split('&').slice(0,5);
                    }
                    // if (row[8].length==0||row[8]==''){
                    //     return '暂无';
                    // }else {
                    //     var tag='';
                    //     for (var k=0;k<row[8].length;k++){
                    //         tag+=row[8][k]+' ';
                    //     }
                    //     return tag;
                    // }
                },
            },
        ],
        onClickCell: function (field, value, row, $element) {
            if ($element[0].cellIndex==0){
                if (row.type=='org'){
                    window.open('/index/organization/?user_id='+row.id);
                }else {
                    window.open('/index/person/?user_id='+row.id);
                }
            }
        },
    });
};

//网络分析
var network_url='/group/group_user_rank/?g_name='+group_name+'&submit_user='+submit_user;
$.ajax({
    url: network_url,
    type: 'GET',
    dataType: 'json',
    async: true,
    success:network
});
var rel_table={
    "join":"参与事件",
    "discuss":"参与舆论",
    "other_relation":"其他关系",
    "contain":"主题关联",
    "event_other":"其他关系",
    "friend":"交互",
    "colleague":"业务关联",
    "organization_tag":"其他关系",
    "friend":"交互",
    "relative":"亲属",
    "leader":"上下级关系",
    "colleague":"自述关联",
    "ip_relation":"IP关联",
    "user_tag":"其他关系",
};
function network(data) {
    var data = eval(data);
    $('#container #content_left .network_analysis .net_detail .detail-1 .det-1').text(data.relation_count);
    $('#container #content_left .network_analysis .net_detail .detail-1 .det-2').text(data.relation_degree.toFixed(2));
    $('#container #content_left .network_analysis .net_detail .detail-1 .det-3').text(data.conclusion);
    var peo=[];
    $.each(data.relation_table,function (index,item) {
        peo.push({
            'uid1':item[0],
            'name1':item[1],
            'relation':item[2],
            'uid2':item[3],
            'name2':item[4],
        })
    })
    $('#network_list').bootstrapTable('load', peo);
    $('#network_list').bootstrapTable({
        data:peo,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 5,//单页记录数
        pageList: [5, 20,],//分页步进值
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
                title: "UID",//标题
                field: "uid1",//键名
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
                field: "name1",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.name1==''||row.name1=='NULL'||row.name1=='unknown'){
                        return row.uid1;
                    }else {
                        return row.name1;
                    }
                }
            },
            {
                title: "关系",//标题
                field: "relation",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.relation==''||row.relation=='NULL'||row.relation=='unknown'){
                        return '未知';
                    }else {
                        return row.relation;
                    }
                },
            },
            {
                title: "UID",//标题
                field: "uid2",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                // formatter: function (value, row, index) {
                //     return row[3];
                // }
            },
            {
                title: "昵称",//标题
                field: "name2",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.name2==''||row.name2=='NULL'||row.name2=='unknown'){
                        return row.uid2;
                    }else {
                        return row.name2;
                    }
                }
            },
        ],
        onClickCell: function (field, value, row, $element) {
            // if ($element[0].cellIndex==0){
            //     window.open('/index/person/?user_id='+row[0]);
            // }else if ($element[0].cellIndex==3){
            //     window.open('/index/person/?user_id='+row[3]);
            // };
        },
    });
};

//=============话题分析
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
require.config({
    paths: {
        echarts: '/static/js/echarts-2/build/dist',
    }
});
//----自动标签
var key_tag_url='/group/group_user_keyowrds/?g_name='+group_name+'&submit_user='+submit_user;
$.ajax({
    url: key_tag_url,
    type: 'GET',
    dataType: 'json',
    async: true,
    success:key_tag
});
var key_series=[],tag_series=[];
function key_tag(data) {
    var data=eval(data);
    $.each(data.keywords,function (index,item) {
        key_series.push(
            {
                name: item[0],
                value: item[1].toFixed(2)*100,
                itemStyle: createRandomItemStyle()
            }
        )
    });
    $.each(data.mark,function (index,item) {
        tag_series.push(
            {
                name: item[0],
                value: item[1].toFixed(2)*100,
                itemStyle: createRandomItemStyle()
            }
        )
    });

if (key_series.length==0){
    $('#tag_left').html('暂无数据');
    $('#tag_left').css({'lineHeight':'330px'});
}else {
    require(
        [
            'echarts',
            'echarts/chart/wordCloud'
        ],
        //关键词
        function (ec) {
            // 基于准备好的dom，初始化echarts图表
            var myChart = ec.init(document.getElementById('tag_left'));

            option = {
                title: {
                    // text: '关键词',
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
                    data: key_series
                }]
            };

            myChart.setOption(option);
            var ecConfig = require('echarts/config');
            myChart.on(ecConfig.EVENT.HOVER, function (param){
                var selected = param.name;
            });
        }
    );
}
if (tag_series.length==0){
    $('#tag_right').html('暂无数据');
    $('#tag_right').css({'lineHeight':'330px'});
}else {
    require(
        [
            'echarts',
            'echarts/chart/wordCloud'
        ],

        //----微话题
        function (ec) {
            // 基于准备好的dom，初始化echarts图表
            var myChart = ec.init(document.getElementById('tag_right'));


            option = {
                title: {
                    // text: '微话题',
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
                    data: tag_series
                }]
            };

            myChart.setOption(option);
            var ecConfig = require('echarts/config');
            myChart.on(ecConfig.EVENT.HOVER, function (param){
                var selected = param.name;
            });
        }
    );
};
};

//============事件分析
var character_url='/group/group_event_rank/?g_name='+group_name+'&submit_user='+submit_user;
$.ajax({
    url: character_url,
    type: 'GET',
    dataType: 'json',
    async: true,
    success:character
});
function character(data) {
    var data = eval(data);
    console.log(data)
    $('#ranking').bootstrapTable('load', data);
    $('#ranking').bootstrapTable({
        data:data,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 5,//单页记录数
        pageList: [5, 10,],//分页步进值
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
            },
            {
                title: "关联人数",//标题
                field: "user",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.user==''||row.user=='NULL'){
                        return 0;
                    }else {
                        return row.user.length;
                    }
                }
            },
            {
                title: "重要度",//标题
                field: "influ",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (value==''||value=='NULL'){
                        return 0;
                    }else {
                        return value.toFixed(2);
                    }
                },
            },
            {
                title: "关联用户",//标题
                field: "user",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.user==''||row.user=='NULL'||row.user.length=='NULL'){
                        return '暂无';
                    }else {
                        var words=row.user;
                        if (words.length<=5){
                            return words.join('\n');
                        }else {
                            var key=words.splice(0,5).join('\n');
                            var tit=words.splice(5).join('\n');
                            return '<p title="'+tit+'">'+key+'</p> ';
                        }
                    }
                },
            },

        ],
        onClickCell: function (field, value, row, $element) {
            if ($element[0].cellIndex==0){
                window.open('/index/event/?user_id='+row.event_id);
            }
        },
    });
};


//----人物自动标签
var user_tag_url='/group/group_user_tag/?g_name='+group_name+'&submit_user='+submit_user;
$.ajax({
    url: user_tag_url,
    type: 'GET',
    dataType: 'json',
    async: true,
    success:user_tag
});
var user_key_series=[],user_tag_series=[];
function user_tag(data) {
    var data = eval(data);
    $.each(data.keywords, function (index, item) {
        user_key_series.push(
            {
                name: item[0],
                value: item[1].toFixed(2) * 100,
                itemStyle: createRandomItemStyle()
            }
        )
    });
    $.each(data.mark, function (index, item) {
        user_tag_series.push(
            {
                name: item[0],
                value: item[1].toFixed(2) * 100,
                itemStyle: createRandomItemStyle()
            }
        )
    });

if (user_key_series.length==0){
    $('#label_left').html('暂无数据');
    $('#label_left').css({'lineHeight':'330px'});
}else {
    require(
        [
            'echarts',
            'echarts/chart/wordCloud'
        ],
        function (ec) {
            // 基于准备好的dom，初始化echarts图表
            var myChart = ec.init(document.getElementById('label_left'));


            option = {
                title: {
                    // text: '关键词',
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
                    data: user_key_series
                }]
            };

            myChart.setOption(option);
            var ecConfig = require('echarts/config');
            myChart.on(ecConfig.EVENT.HOVER, function (param){
                var selected = param.name;
            });
        }
    );
}

if (user_tag_series.length==0){
    $('#label_right').html('暂无数据');
    $('#label_right').css({'lineHeight':'330px'});
}else {
    //----人物业务标签
    require(
        [
            'echarts',
            'echarts/chart/wordCloud'
        ],
        function (ec) {
            // 基于准备好的dom，初始化echarts图表
            var myChart = ec.init(document.getElementById('label_right'));

            option = {
                title: {
                    // text: '微话题',
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
                    data:user_tag_series
                }]
            };

            myChart.setOption(option);
            var ecConfig = require('echarts/config');
            myChart.on(ecConfig.EVENT.HOVER, function (param){
                var selected = param.name;
            });
        }
    );
}
}

