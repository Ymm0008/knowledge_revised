var url = '/sysadmin/topic/get_data';
$.ajax({
    url: url,
    type: 'GET',
    dataType:'json',
    async:true,
    success:draw_table
});

    function draw_table(data){
        var data=eval(data);
        $('#sysadmin_topic_table').bootstrapTable('load',data)
        $('#sysadmin_topic_table').bootstrapTable({
            data:data,
            search: true,//是否搜索
            pagination: true,//是否分页
            pageSize: 5,//单页记录数
            pageList: [5, 15],//分页步进值
            sidePagination: "client",//服务端分页
            searchAlign: "left",
            searchOnEnterKey: true,//回车搜索
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
                title: "专题名称",//标题
                field: "name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                visible:true,
            },
            {
                title: "事件数量",//标题
                field: "count",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "创建时间",//标题
                field: "time",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "自动标签",//标题
                field: "auto_label",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (value.length==0)
                        return '暂无';
                    else
                        return value;
                },
            },
            {
                title: "业务标签",//标题
                field: "buss_label",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (value.length==0||(value.length==1&&value[0]==''))
                        return '暂无';
                    else
                        return value;
                },
            },
            {
                title: "专题查看",//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value,row) {
                    var addr = '<a href="/theme/result/?theme_name='+row.name+'" target="_blank"><span style="text-decoration:underline;font-weight:bold;">查看专题</span></a>'
                    return addr;
                },
            }
            ]
        });
        $('#table-user-contain').css("display","block");
        $('#table-user-contain').css("margin-right","10px");
    }