//包含事件
var things_url='/theme/theme_detail/?theme_name='+theme_name+'&submit_user='+submit_user;
$.ajax({
    url: things_url,
    type: 'GET',
    dataType: 'json',
    async: true,
    success:things
});
function things(data) {
    var data = eval(data);
    var things=[];
    $.each(data,function (index,item) {
        things.push({
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
    $('#things').bootstrapTable('load', things);
    $('#things').bootstrapTable({
        data:things,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 5,//单页记录数
        pageList: [5, 10],//分页步进值
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
                    if (row.event_type==''||row.event_type=='NULL'||row.event_type=='unknown'||row.event_type=='null'){
                        return '暂无';
                    }else {
                        if (row.event_type=='other'){
                            return '其他';
                        }else {
                            return row.event_type;
                        }
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
                    if (row.date==''||row.date=='NULL'||row.date=='unknown'||row.date=='null'){
                        return '暂无';
                    }else {
                        return row.date;
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
                    if (row.location==''||row.location=='NULL'||row.location=='unknown'||row.location=='null'){
                        return '暂无';
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
                    if (row.people==''||row.people=='NULL'||row.people=='unknown'||row.people=='null'){
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
                    if (row.weibo==''||row.weibo=='NULL'||row.weibo=='unknown'||row.weibo=='null'){
                        return '暂无';
                    }else {
                        return row.weibo;
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
                    if (row.keywords.length==0||row.keywords==''||row.keywords=='null'){
                        return '暂无';
                    }else {
                        var words=row.keywords;
                        words.removeByValue('');
                        if (words.length<=5){
                            return words.join(',');
                        }else {
                            var key=words.splice(0,5).join(',');
                            var tit=words.splice(5).join(',');
                            return '<p title="'+tit+'">'+key+'</p> ';
                        }
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
                    if (row.label.length==0||row.label==''||row.label=='null'){
                        return '暂无';
                    }else {
                        var words=row.label;
                        words.removeByValue('');
                        if (words.length<=5){
                            return words.join(',');
                        }else {
                            var key=words.splice(0,5).join(',');
                            var tit=words.splice(5).join(',');
                            return '<p title="'+tit+'">'+key+'</p> ';
                        }
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
//删除指定项
Array.prototype.removeByValue = function(val) {
    for(var i=0; i<this.length; i++) {
        if(this[i] == val) {
            this.splice(i, 1);
            break;
        }
    }
};


//时间分析--鱼骨图
var fish_url='/theme/theme_analysis_flow/?theme_name='+theme_name+'&submit_user='+submit_user;
$.ajax({
    url: fish_url,
    type: 'GET',
    dataType: 'json',
    async: true,
    success:fish
});

function fish(data) {
    var data=eval(data);
    var finshdata = '';
    $.each(data,function (index,item) {
        if (index%2 == 0){
            finshdata+=
                '<div class="fish_item">'+
                '   <ul class="top">'+
                // '       <li class="weibo" title="'+item[0]+'" style="border-left: 1px solid rgb(248, 151, 130);">事件ID：'+item[0]+'</li>'+
                '       <li class="weibo" title="'+item[1]+'" style="height: 86px;white-space: normal;border-left: 1px solid rgb(248, 151, 130);">微博内容：'+item[1]+'</li>'+
                '       <li class="weibo" title="'+item[2]+'" style="border-left: 1px solid rgb(248, 151, 130);">时间：'+item[2]+'</li>'+
                '       <li class="line-last line-point" style="background-position: 0px 0px;"></li>'+
                '   </ul>'+
                '</div>';
        }else {
            finshdata+=
                '<div class="fish_item" style="top:122px;">'+
                '   <ul class="bottom">'+
                // '       <li class="weibo" title="'+item[0]+'" style="border-left: 1px solid rgb(26, 132, 206);">事件ID：'+item[0]+'</li>'+
                '       <li class="weibo" title="'+item[1]+'" style="height: 86px;white-space: normal;border-left: 1px solid rgb(26, 132, 206);">微博内容：'+item[1]+'</li>'+
                '       <li class="weibo" title="'+item[2]+'" style="border-left: 1px solid rgb(26, 132, 206);">时间：'+item[2]+'</li>'+
                '       <li class="line-last line-point" style="background-position: 0px -20px;"></li>'+
                '   </ul>'+
                '</div>';
        }
    })
    $(".fishBone .fish_box").append(finshdata);
    var _p=0;
    var fish_length=data.length;
    $('#container .fishBone .fish_box').width(fish_length*180);
    var fish_width=fish_length*180;
    $('#container .fishBone .prev').on('click',function () {
        _p+=180;
        if (fish_length<=3){
            alert('没有其他卡片内容了。');
        }else {
            var fishbone=$(".fishBone .fish_box");
            var step1=_p;
            if (step1 > 0 ){
                alert('没有其他内容了。');
                _p=0;
            }else {
                $(fishbone).css({
                    "-webkit-transform":"translateX("+step1+"px)",
                    "-moz-transform":"translateX("+step1+"px)",
                    "-ms-transform":"translateX("+step1+"px)",
                    "-o-transform":"translateX("+step1+"px)",
                    "transform":"translateX("+step1+"px)",
                });
            }
        }
    });
    $('#container .fishBone .next').on('click',function () {
        _p-=180;
        if (fish_length<=3){
            alert('没有其他卡片内容了。');
        }else {
            var step2=_p;
            var fishbone=$(".fishBone .fish_box");
            if (step2 <= (-fish_width+500)){
                alert('没有其他内容了');
                _p=180;
            }else {
                $(fishbone).css({
                    "-webkit-transform":"translateX("+step2+"px)",
                    "-moz-transform":"translateX("+step2+"px)",
                    "-ms-transform":"translateX("+step2+"px)",
                    "-o-transform":"translateX("+step2+"px)",
                    "transform":"translateX("+step2+"px)",
                });

            };
        }
    });


}


//地域分析
var place_url='/theme/theme_analysis_geo/?theme_name='+theme_name+'&submit_user='+submit_user;
$.ajax({
    url: place_url,
    type: 'GET',
    dataType: 'json',
    async: true,
    success:place
});
function place(data) {
    var data=eval(data);
    var place_x=[],place_series=[],legends=[];
    $.each(data.top_city,function (index,item) {
        place_x.push(item);
    })
    for (var key in data.event_city){
        legends.push(key);
        place_series.push(
            {
                name: key,
                type: 'bar',
                stack: '数量',
                label: {
                    normal: {
                        show: true,
                        position: 'insideRight'
                    }
                },
                data: data.event_city[key]
            }
        )
    }
    var myChart = echarts.init(document.getElementById('area'));
    var option = {
        tooltip : {
            trigger: 'axis',
            axisPointer : {            // 坐标轴指示器，坐标轴触发有效
                type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            }
        },
        legend: {
            data: legends
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom:'0',
            top: '42%',
            containLabel: true
        },
        xAxis:  {
            type: 'category',
            data: place_x
        },
        yAxis: {
            type: 'value'
        },
        series: place_series
    };
    myChart.setOption(option);
}

//网络分析
var network_url='/theme/theme_analysis_net/?theme_name='+theme_name+'&submit_user='+submit_user;
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
    var net=[];
    $.each(data.relation_table,function (index,item) {
        net.push({
            'event_name1':item[0],
            'event_name2':item[2],
            'relation':item[1],
        })
    })
    $('#network_list').bootstrapTable('load', net);
    $('#network_list').bootstrapTable({
        data:net,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 5,//单页记录数
        pageList: [5, 15],//分页步进值
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
                field: "event_name1",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                // formatter: function (value, row, index) {
                //     return row[0];
                // }
            },
            {
                title: "关系",//标题
                field: "relation",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.relation==''||row.relation=='unknown'||row.relation=='NULL'){
                        return '未知';
                    }else {
                        return row.relation;
                    }
                }
            },
            {
                title: "事件名称",//标题
                field: "event_name2",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                // formatter: function (value, row, index) {
                //     return row[2];
                // },
            },
        ],
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
var key_tag_url='/theme/theme_analysis_keywords/?theme_name='+theme_name+'&submit_user='+submit_user;
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
                value: item[1].toFixed(2) *100,
                itemStyle: createRandomItemStyle()
            }
        )
    });
    $.each(data.hashtag,function (index,item) {
        tag_series.push(
            {
                name: item[0],
                value: item[1].toFixed(2) *100,
                itemStyle: createRandomItemStyle()
            }
        )
    });
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
}


//============人物分析
var character_url='/theme/theme_analysis_user_rank/?theme_name='+theme_name+'&submit_user='+submit_user;
$.ajax({
    url: character_url,
    type: 'GET',
    dataType: 'json',
    async: true,
    success:character
});
function character(data) {
    var data = eval(data);
    $('#ranking').bootstrapTable('load', data);
    $('#ranking').bootstrapTable({
        data:data,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 5,//单页记录数
        pageList: [5, 20, 40, 80],//分页步进值
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
                field: "id",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "人物名",//标题
                field: "name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (value==''||value=='NULL'){
                        return row.id;
                    }else {
                        return row.name;
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
                title: "参与事件数量",//标题
                field: "related_event",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.related_event==''||row.related_event=='NULL'){
                        return 0;
                    }else {
                        return row.related_event.length;
                    }
                },
            },
            {
                title: "参与事件",//标题
                field: "related_event",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.related_event==''||row.related_event=='NULL'){
                        return '暂无事件';
                    }else {
                        var event=row.related_event;
                        if (event.length<=2){
                            return event.join(',');
                        }else {
                            var key=event.splice(0,2).join(',');
                            var tit=event.splice(2).join('\n');
                            return '<p title="'+tit+'">'+key+'</p> ';
                        }
                    }
                },
            },
        ],
        onClickCell: function (field, value, row, $element) {
            if ($element[0].cellIndex==0){
                if (row.node_type == 'org'){
                    window.open('/index/organization/?user_id='+row.id);
                }else {
                    window.open('/index/person/?user_id='+row.id);
                }
            }
        }
    });
};
//----人物自动标签
var user_tag_url='/theme/theme_analysis_user_tag/?theme_name='+theme_name+'&submit_user='+submit_user;
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
                value: item[1].toFixed(2)  * 100,
                itemStyle: createRandomItemStyle()
            }
        )
    });

if (user_key_series.length==0){
    $('#label_left').html('暂无数据');
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
            })
        }
    );
}

//----人物业务标签

if (user_tag_series.length==0){
    $('#label_right').html('暂无数据');
}else {
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
};


