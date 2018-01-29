/**
 * Created by apple on 18/5/17.
 */
function getRole(role,role_type){
    var url='/api/fee/withdraw';
    var _params={
        role:role,
        role_type:role_type
    };

    var roleVal;

    $.ajax({
        type: 'GET',
        dataType: 'json',
        data:_params,
        url: url,
        async:false,
        beforeSend: function (XMLHttpRequest) {
        },
        success: function (res) {
            roleVal=res;
        },
        complete: function (XMLHttpRequest, textStatus) {
        },
        error: function (xhr) {
            roleVal={}
        }

    });
    return roleVal;
}


