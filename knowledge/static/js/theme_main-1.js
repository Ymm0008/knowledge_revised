//专题概览
var theme_overview_url='/theme/theme_overview/?submit_user='+submit_user;
$.ajax({
    url:theme_overview_url,
    type: 'GET',
    dataType: 'json',
    async: true,
    success:theme_overview
});
function theme_overview(data) {
    var data = eval(data);
    var theme_all=[];
    $.each(data,function (index,item) {
        theme_all.push({
            'name':item[1],
            'include':item[2],
            'time':item[5],
            'keywords':item[3],
            'label':item[4],
        })
    })
    $('#theme_list').bootstrapTable('load', theme_all);
    $('#theme_list').bootstrapTable({
        data:theme_all,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 5,//单页记录数
        pageList: [5,10,15],//分页步进值
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
                title: "专题名称",//标题
                field: "name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                // formatter: function (value, row, index) {
                //     return row[1];
                // }
            },
            {
                title: "包含事件",//标题
                field: "include",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                // formatter: function (value, row, index) {
                //     return row[2];
                // }
            },
            {
                title: "创建时间",//标题
                field: "time",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                // formatter: function (value, row, index) {
                //     return row[5];
                // },
            },
            {
                title: "自动标签",//标题
                field: "keywords",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.keywords.length==0){
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
                    if (row.label.length==0||(row.label.length==1&&row.label[0]=="")){
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
            {
                title: "查看专题",//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    return '<a style="cursor: pointer;">查看专题</a>';
                },
            },
            {
                title: '编辑专题',//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    return '<a style="cursor: pointer;">编辑专题</a>';
                },
            },
            //多选框
            {
                title: "专题对比",//标题
                field: "select",
                checkbox: true,
                align: "center",//水平
                valign: "middle"//垂直
            },

        ],
        onCheck:function (row) {
            theme_diff.push(row.name);
            if (theme_diff.length>1){
                $('#container .group_operating .compared').css({color:'#337ab7'});
            }else {
                $('#container .group_operating .compared').css({color:'#9c9c9c'});
            }
        },
        onUncheck:function (row) {
            theme_diff.removeByValue(row.name);
            if (theme_diff.length>1){
                $('#container .group_operating .compared').css({color:'#337ab7'});
            }else {
                $('#container .group_operating .compared').css({color:'#9c9c9c'});
            }
        },
        onCheckAll:function (row) {
            theme_diff.push(row.name);
            if (theme_diff.length>1){
                $('#container .group_operating .compared').css({color:'#337ab7'});
            }else {
                $('#container .group_operating .compared').css({color:'#9c9c9c'});
            }
        },
        onUncheckAll:function (row) {
            theme_diff.removeByValue(row.name);
            if (theme_diff.length>1){
                $('#container .group_operating .compared').css({color:'#337ab7'});
            }else {
                $('#container .group_operating .compared').css({color:'#9c9c9c'});
            }
        },
        onClickCell: function (field, value, row, $element) {
            if ($element[0].innerText=='查看专题') {
                window.open('/theme/result/?theme_name='+row.name);
            }else if ($element[0].innerText=='编辑专题') {
                window.open('/theme/modify/?theme_name='+row.name);
            }
        }
    });
};

var theme_diff=[];
$('#container .group_operating .operating .compared').on('click',function () {
    if ($(this).css('color')=='rgb(51, 122, 183)'){
        if (theme_diff.length==2){
            window.open('/theme/compare/?theme_name1='+theme_diff[0]+'&theme_name2='+theme_diff[1]);
        }else {
            alert('请您注意选择的专题，您只能选择2个。(请检查您勾选的专题)')
        }
    }
});

//删除指定项
Array.prototype.removeByValue = function(val) {
    for(var i=0; i<this.length; i++) {
        if(this[i] == val) {
            this.splice(i, 1);
            break;
        }
    }
};

