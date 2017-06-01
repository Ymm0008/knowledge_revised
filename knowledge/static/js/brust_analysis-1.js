//时间戳转换
Array.prototype.contains = function (obj) {
    var i = this.length;
    while (i--) {
        if (this[i] === obj) {
            return true;
        }
    }
    return false;
}
//===
var ajax_method;
function sudden() {
    ajax_method='GET';
}
sudden.prototype= {
    call_request:function(url,callback) {
        $.ajax({
            url: url,
            type: ajax_method,
            dataType: 'json',
            async: true,
            success:callback
        });
    },
};

function current(data) {
    var data=eval(data);
    var weibo_str='';
    var name,time,photo,text,key_words='';
    if(data.nick_name==''||data.nick_name=='unknown'
        ||data.nick_name=='null'||data.nick_name== undefined ){
        name=data.uid;
    }else {
        name=data.nick_name;
    };
    if(data.timestamp==''||data.timestamp=='unknown'
        ||data.timestamp=='null'||data.timestamp== undefined){
        time='暂无';
    }else {
        time=getLocalTime(data.timestamp);
    };
    if(data.photo_url==''||data.photo_url=='unknown'
        ||data.photo_url== undefined ||data.photo_url=='null'){
        photo='/static/images/unknown.png';
    }else {
        photo=data.photo_url;
    };
    if(data.text==''||data.text=='unknown'
        ||data.text=='null'||data.text== undefined){
        text='暂无';
    }else {
        text=data.text;
    };
    if(data.keywords_string==''||data.keywords_string=='unknown'
        ||data.keywords_string=='null'||data.keywords_string== undefined){
        key_words='暂无';
    }else {
        var word=data.keywords_string.split('&');
        if (word.length>5){
            for (var kw=0;kw<5;kw++){
                key_words+='<a>'+word[kw]+'</a> ';
            }
        }else {
            for (var kw=0;kw<word.length;kw++){
                key_words+='<a>'+word[kw]+'</a> ';
            }
        }
    }
    weibo_str+=
        '<div class="weibo" style="padding:8px 10px;">'+
        '    <div class="user">'+
        '        <div class="user_left">'+
        '             <img src="'+photo+'" alt="">'+
        '        </div>'+
        '        <div class="user_right">'+
        '              <a href="###" class="user_name">'+name+'</a>&nbsp;<span>于</span>'+
        '              <b class="time">'+time+'</b>&nbsp;<span>发表：</span>'+
        '           <span class="speech">'+text+'</span>'+
        '           <p class="fd_nums">'+
        '               <span>转发数:</span><b class="f_amount">'+data.retweeted+'</b>'+
        '               <span>评论数:</span><b class="d_amount">'+data.comment+'</b>'+
        '           </p>'+
        '        </div>'+
        '    </div>'+
        '</div>';
    $('.weibo_content').append(weibo_str);
    $('.forecast_content .time').text(getLocalTime(data.detect_ts));
    $('.forecast_content .people').text(Math.round(data.uid_prediction));
    $('.forecast_content .weibo_count').text(Math.round(data.weibo_prediction));
    //画图
    var data=data.trendline;
    console.log(data)
    var myChart = echarts.init(document.getElementById('forecast_img'));
    var series_nums=[],series_time=[];
    var climax = data.climax;

    var exist_trend = data.exist_trend;
    var rise_trend = data.rise_trend;
    var fall_trend = data.fall_trend;
    var max_time=[],max_nums=[],
        exist_time=[],exist_nums=[],
        rise_time=[],rise_nums=[],
        fall_time=[],fall_nums=[];

    if (climax.length!=0){
        max_time.push(climax[0]);
        max_nums.push(climax[1]);
    };

    if (exist_trend.length!=0){
        for (var i=0; i< exist_trend.length; i++){
            exist_time.push(exist_trend[i][0]);
            exist_nums.push(exist_trend[i][1]);
        };
    };

    if (rise_trend.length!=0){
        for (var i=0; i< rise_trend.length; i++){
            rise_time.push(rise_trend[i][0]);
            rise_nums.push(rise_trend[i][1].toFixed(2));
        };
    };

    if (fall_trend.length!=0){
        for (var i=0; i< fall_trend.length; i++){
            fall_time.push(fall_trend[i][0]);
            fall_nums.push(fall_trend[i][1].toFixed(2));
        };
    };

    var rel_len=exist_time.length;
    var rise_len=rise_time.length;
    var fall_len=fall_time.length;
    var rel_last;
    if (rel_len!=0){
        rel_last=exist_nums[rel_len-1];
        var not_type1='none';
        if (exist_time.contains(max_time[0])){
            not_type1='pin';
        }
        series_nums.push(
            {
                name:'宏观趋势预测',
                type:'line',
                smooth:true,
                itemStyle: {
                    color:'#FF7F50',
                    normal: {
                        color: '#FF7F50',
                    }
                },
                data:exist_nums,
                markPoint : {
                    symbol: not_type1,//symbol: 'pin',
                    data : [
                        {type : 'max', name: '最大值'},
                    ]
                },
            }
        );
    };
    if (rise_len!=0){
        if (rel_len!=0){
            rise_nums.unshift(rel_last);
            for (var t=0;t<rel_len-1;t++){
                rise_nums.unshift('-');
            }
        };
        var not_type2='none';
        if (rise_time.contains(max_time[0])){
            not_type2='pin';
        }
        series_nums.push(
            {
                name:'宏观趋势攀高',
                type:'line',
                itemStyle:{
                    normal:{
                        color:'red',
                        lineStyle:{
                            color: 'red',
                            type:'dotted'
                        },
                    },

                },
                data:rise_nums,
                markPoint : {
                    symbol: not_type2,//symbol: 'pin',
                    data : [
                        {type : 'max', name: '最大值'},
                    ]
                },
            }
        );
    };
    if (fall_len!=0){
        if (rel_len!=0&&rise_len!=0){
            fall_nums.unshift(rise_nums[rise_nums-1]);
            for (var t=0;t<(rel_len+rise_len-2);t++){
                fall_nums.unshift('-');
            }
        }else if (rel_len!=0 && rise_len==0){
            fall_nums.unshift(exist_nums[rel_len-1]);
            for (var t=0;t<rel_len-1;t++){
                fall_nums.unshift('-');
            }
        }else if (rise_len!=0&&rel_len==0){
            fall_nums.unshift(rise_nums[rel_len-1]);
            for (var t=0;t<rise_len-1;t++){
                fall_nums.unshift('-');
            }
        }
        var not_type3='none';
        if (fall_time.contains(max_time[0])){
            not_type3='pin';
        }
        series_nums.push(
            {
                name:'宏观趋势走低',
                type:'line',
                itemStyle:{
                    normal:{
                        color:'green',
                        lineStyle:{
                            color: 'green',
                            type:'dotted'
                        },
                    }
                },
                data:fall_nums,
                markPoint : {
                    symbol: not_type3,//symbol: 'pin',
                    data : [
                        {type : 'max', name: '最大值'},
                    ]
                },
            }
        );
    };
    var _time=exist_time.concat(rise_time).concat(fall_time);
    $.each(_time,function (index,item) {
        series_time.push(getLocalTime(item));
    })

    var option = {
        title : {
            // text: '某楼盘销售情况',
            // subtext: '纯属虚构'
        },
        tooltip : {
            trigger: 'axis',
            formatter:function (v) {
                if (v[0].value!=undefined){
                    return v[0].seriesName + '<br/>'+v[0].name+'<br/>'+v[0].value;
                }
                if (v[1].value!=undefined){
                    return v[1].seriesName + '<br/>'+v[1].name+'<br/>'+v[1].value;
                }
                if (v[2].value!=undefined){
                    return v[2].seriesName + '<br/>'+v[2].name+'<br/>'+v[2].value;
                }
            }
        },
        legend: {
            data:['宏观趋势预测','宏观趋势攀高','宏观趋势走低']
        },
        calculable : true,
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                data: series_time,
                axisLabel: {
                    textStyle: {
                        color: 'black',
                        fontFamily: '微软雅黑',
                        fontSize: 14,
                    },
                }
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel: {
                    formatter: '{value} 次',
                    textStyle: {
                        color: 'black',
                        fontFamily: '微软雅黑',
                        fontSize: 14,
                    },
                }
            }
        ],
        series : series_nums
    };
    // 为echarts对象加载数据
    myChart.setOption(option);

}


//===========================================
var sudden=new sudden();
function analysis() {
    var url = '/brust/show_weibo_bursting/?mid='+mid;
    sudden.call_request(url,current);
    var weibo_url = '/brust/show_current_hot_weibo/?mid='+mid;
    sudden.call_request(weibo_url,forward_discussion);
}
analysis();

function getLocalTime(nS) {
    return new Date(parseInt(nS) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日|上午|下午/g, " ");
}
// ===微博=========================
var f_d_data;
function forward_discussion(data){
    var data=eval(data);
    f_d_data=data;
    _wei_f_D(f_d_data.hot_retweeted);
}
$('#forward').on('click',function () {
    _wei_f_D(f_d_data.hot_retweeted);
});
$('#discussion').on('click',function () {
    _wei_f_D((f_d_data.hot_comment));
});
function _wei_f_D(data) {
    $('#weibo').empty();
    var weibo_str='';
    for (var w=0;w<data.length;w++){
        var name,time,photo,text;
        if(data[w].nick_name==''||data[w].nick_name=='unknown'
            ||data[w].nick_name=='null'||data[w].nick_name== undefined ){
            name=data[w].uid;
        }else {
            name=data[w].nick_name;
        };
        if(data[w].timestamp==''||data[w].timestamp=='unknown'
            ||data[w].timestamp=='null'||data[w].timestamp== undefined){
            time='暂无';
        }else {
            time=getLocalTime(data[w].timestamp);
        };
        if(data[w].photo_url==''||data[w].photo_url=='unknown'
            ||data[w].photo_url== undefined ||data[w].photo_url=='null'){
            photo='/static/images/unknown.png';
        }else {
            photo=data[w].photo_url;
        };
        if(data[w].text==''||data[w].text=='unknown'
            ||data[w].text=='null'||data[w].text== undefined){
            text='暂无';
        }else {
            text=data[w].text;
        };
        weibo_str+=
            '<div class="weibo" style="padding:8px 10px;">'+
            '    <div class="user">'+
            '        <div class="user_left">'+
            '             <img src="'+photo+'" alt="">'+
            '        </div>'+
            '        <div class="user_right">'+
            '           <a href="###" class="user_name">'+name+'</a>&nbsp;<span>于</span>'+
            '           <b class="time">'+time+'</b>&nbsp;<span>发表：</span>'+
            '           <span class="speech">'+text+'</span>'+
            '           <p class="fd_nums">'+
            '               <span>转发数:</span><b class="f_amount">'+data[w].retweeted+'</b>'+
            '               <span>评论数:</span><b class="d_amount">'+data[w].comment+'</b>'+
            '           </p>'+
            '        </div>'+
            '    </div>'+
            '</div>';
    };
    $('#weibo').append(weibo_str);
}



