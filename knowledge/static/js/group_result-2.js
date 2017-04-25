//右边框------关联
var link_url='/group/group_related/?g_name='+group_name+'&submit_user='+submit_user;
$.ajax({
    url: link_url,
    type: 'GET',
    dataType: 'json',
    async: true,
    success:link_source
});
function link_source(data) {
    var data=eval(data);
    //关联人物
    var user=[];
    if (data.final_user.length==0 || (data.final_user.length==1&&data.final_user[0]=='')){
        $('.link_user .users').append(
            '<a>无数据</a>'
        );
    }else {
        $.each(data.final_user,function (index,item) {
            if (index<=4){
                $('.link_user .users').append(
                    '<a title="'+item[1]+'"><b style="display: none;">'+item[0]+'</b>'+item[1]+'</a>'
                );
            };
            if(!isNaN(item[0])) {
                user.push(item[0]);
            }
        });
        $('.link_user .users a').on('click',function () {
            window.open('/index/person/?user_id='+$(this).find('b').text());
        })
    }
    //关联事件
    var event=[];
    if (data.final_event.length==0|| (data.final_event.length==1&&data.final_event[0]=='')){
        $('.link_event .events').append(
            '<a>无数据</a>'
        )
    }else {
        $.each(data.final_event,function (index,item) {
            if (index<=4){
                $('.link_event .events').append(
                    '<a title="'+item[1]+'"><b style="display: none;">'+item[0]+'</b>'+item[1]+'</a>'
                )
            }
            event.push(item[0]);
        });
        $('.link_event .events a').on('click',function () {
            window.open('/index/event/?user_id='+$(this).find('b').text());
        })
    }

    //关联机构
    var org=[];
    if (data.final_org.length==0|| (data.final_org.length==1&&data.final_org[0]=='')){
        $('.link_agency .agencys').append(
            '<a>无数据</a>'
        )
    }else {
        $.each(data.final_org,function (index,item) {
            if (index<=4){
                $('.link_agency .agencys').append(
                    '<a title="'+item[1]+'"><b style="display: none;">'+item[0]+'</b>'+item[1]+'</a>'
                )
            }
            if(!isNaN(item[0])) {
                org.push(item[0]);
            }
        });
        $('.link_agency .agencys a').on('click',function () {
            window.open('/index/organization/?user_id='+$(this).find('b').text());
        })
    }

    //关联知识
    var wiki=[];
    if (data.final_wiki.length==0|| (data.final_wiki.length==1&&data.final_wiki[0]=='')){
        $('.link_knowledge .knowledge').append(
            '<a>无数据</a>'
        )
    }else {
        $.each(data.final_wiki,function (index,item) {
            if (index<=4){
                $('.link_knowledge .knowledge').append(
                    // '<a title="'+item[0]+'" href="'+item[1]+'">'+item[0]+'</a>'
                    '<a title="'+item[0]+'" href="###">'+item[0]+'</a>'
                )
            }else {
                wiki.push(
                    // '<a title="'+item[0]+'" href="'+item[1]+'">'+item[0]+'</a>'
                    '<a title="'+item[0]+'" href="###">'+item[0]+'</a>'
                )
            }
        });
        $('.link_knowledge .knowledge a').on('click',function () {
            window.open('/construction/wiki/?_id='+$(this).text());
        });
    }

    //关联资源
    var file=[];
    if (data.final_file.length==0|| (data.final_file.length==1&&data.final_file[0]=='')){
        $('.link_resources .resources').append(
            '<a>无数据</a>'
        )
    }else {
        $.each(data.final_file,function (index,item) {
            if (index<=4){
                $('.link_resources .resources').append(
                    '<a title="'+item[0]+'" href="'+item[1]+'">'+item[0]+'</a>'
                )
            }
                file.push(
                    '<a title="'+item[0]+'" href="'+item[1]+'">'+item[0]+'</a>'
                )
        });
    }

    //-------人物------
    $('#container #content_right .link_user .user_more').on('click',function () {
        window.open('/index/cards/?user_id='+user+'&node_type=4&card_type=1');
    });

    //------事件-----
    $('#container #content_right .link_event .event_more').on('click',function () {
        window.open('/index/cards/?user_id='+event+'&node_type=4&card_type=2');
    });

    //-----机构-----
    $('#container #content_right .link_agency .agency_more').on('click',function () {
        window.open('/index/cards/?user_id='+org+'&node_type=4&card_type=0');
    });

    //-----知识-----
    $('#container #content_right .link_knowledge .knowledge_more').on('click',function () {
        $('#link .tit_h4').empty().text('关联知识');
        $('#link #link_content').empty();
        if (org.length==0){
            $('#link #link_content').text('没有更多数据');
        }else {
            for (var w=0;w<wiki.length;w++){
                $('#link #link_content').append(wiki[w]);
            }
        }
        $('#link').modal('show');
        $('#link a').on('click',function () {
            window.open('/construction/wiki/?_id='+$(this).text());
        })
    });

    //-----资源-----
    $('#container #content_right .link_resources .resources_more').on('click',function () {
        $('#link .tit_h4').empty().text('关联资源');
        $('#link #link_content').empty();
        if (file.length==0){
            $('#link #link_content').text('没有更多数据');
        }else {
            for (var f=0;f<file.length;f++){
                $('#link #link_content').append(file[f]);
            }
        }
        $('#link').modal('show');
    });

};
