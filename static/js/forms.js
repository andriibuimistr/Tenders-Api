//Generate random id
var randomString = function(length) {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for(var i = 0; i < length; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}


//Convert form data to json
function ConvertFormToJSON(form){
    var array = jQuery(form).serializeArray();
    var json = {};

    jQuery.each(array, function() {
        json[this.name] = this.value || '';
    });

    return json;
}

//Add tender to company
$(function() {
    $('.tender-company-button').click(function() {
        $(this).prop('disabled', true);
        var tid  = $(this).closest("form").attr('id');
		var form = $(this).closest("form");
        $.ajax({
            url: '/tenders/' + tid + '/company',
            data: $(this).closest('form').serialize(),
            type: 'POST',
            success: function(data) {
                form.parent().html(data);
                $('.tender-company-button').removeAttr("disabled");
            },
            error: function (jqXHR, textStatus, errorThrown) {
            	alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                $('.tender-company-button').removeAttr("disabled");
            }
        });
    });
});


//Create tender
$(function() {
    var jsonPrettyPrint = {
        replacer: function (match, pIndent, pKey, pVal, pEnd) {
            var key = '<span class=json-key>';
            var val = '<span class=json-value>';
            var str = '<span class=json-string>';
            var r = pIndent || '';
            if (pKey)
                r = r + key + pKey.replace(/[": ]/g, '') + '</span>: ';
            if (pVal)
                r = r + (pVal[0] == '"' ? str : val) + pVal + '</span>';
            return r + (pEnd || '');
        },
        toHtml: function (obj) {
            var jsonLine = /^( *)("[\w]+": )?("[^"]*"|[\w.+-]*)?([,[{])?$/mg;
            return JSON.stringify(obj, null, 3)
                .replace(/&/g, '&amp;').replace(/\\"/g, '&quot;')
                .replace(/</g, '&lt;').replace(/>/g, '&gt;')
                .replace(jsonLine, jsonPrettyPrint.replacer);
        }
    };

    $('#createTender').click(function() {
        //$(this).prop('disabled', true);
        var form = $("#create-tender");
        var request_id = randomString(32);
        var procedure = $("#create-tender select[name=procurementMethodType]").val();
        var expected_status = $("#create-tender select[name=tenderStatus]").val();
        var json_for_wait = {"Procedure": procedure, "Expected_Tender_Status": expected_status, "Request_Status": "Waiting for response"};
        $('#created_tender_json').prepend('<div class="response-content" id="' + request_id + '">' + jsonPrettyPrint.toHtml(json_for_wait) + '</div>');
        $.ajax({
            url: '/api/tenders',
            dataType : 'json',
            crossDomain: true,
            data: form.serialize(),
            type: 'POST',
            success: function(data) {
                $('#' + request_id).addClass('response-content-success');
                $('#' + request_id).empty();
                $('#' + request_id).prepend('<button class="delete-alert" type="button">x</button>' + jsonPrettyPrint.toHtml(data));
                //$('#createTender').removeAttr("disabled");
            },
            error: function (jqXHR) {
                //$("#created_tender_json").html(JSON.parse(jqXHR.responseText));
                //alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                $('#' + request_id).addClass('response-content-error');
                $('#' + request_id).empty();
                $('#' + request_id).append('<button class="delete-alert" type="button">x</button>' + jsonPrettyPrint.toHtml(JSON.parse(jqXHR.responseText)));
                //$('#createTender').removeAttr("disabled");
            }
        });
    });
});


//Clear created tender response json
$(function() {
    $('#clear-createTender-response').click(function() {
        $("#created_tender_json").empty();
    });
});

//Synchronization tenders
$(function() {
    $('#synchronization').click(function() {
        $(this).prop('disabled', true);
        var alert = $("#alert");
        $.ajax({
            url: '/tenders/synchronization',
            type: 'PATCH',
            success: function(data, textStatus, xhr) {
                alert.html(xhr.status + ' ' + textStatus);
                alert.prop('class', "response-json alert-green");
                $('#synchronization').removeAttr("disabled");
                alert.fadeIn(500).delay(2000).fadeOut(1500);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                //alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                alert.html(jqXHR.status + ' ' + errorThrown.toLowerCase());
                $('#synchronization').removeAttr("disabled");
                alert.prop('class', "response-json alert-red");
                alert.fadeIn(500).delay(2000).fadeOut(1500);
            }
        });
    });
});


//Delete alert in "console"

$(function() {
    $('.delete-alert').click(function() {
        console.log('45614515');
    });
});

$(document).on("click",".delete-alert", function(){
    $(this).closest('div').remove();
});

