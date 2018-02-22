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
        var html_for_wait = '<div class="alert-response-status">Waiting for response</div>' +
                            '<div class="alert-response-description">' +
                                '<div class="wait-procedure-type"><span>Procedure: </span>' + procedure + '</div>' +
                                '<div class="wait-tender-status"><span>Expected Tender Status: </span>' + expected_status + '</div>' +
                            '</div>'
                            ;
        $('#created_tender_json').prepend('<div class="response-content response-content-waiting" id="' + request_id + '">' + html_for_wait + '</div>');
        $.ajax({
            url: '/api/tenders',
            dataType : 'json',
            crossDomain: true,
            data: form.serialize(),
            type: 'POST',
            success: function(data, textStatus, xhr) {
                var operation_status = data.status;
                var tender_status = data.tenderStatus;
                var tender_to_company_status = data.tender_to_company[0].status;
                var tender_id = data.id;
                var tender_link = data.tender_to_company[1];
                $('#' + request_id).addClass('response-content-success').toggleClass( "response-content-waiting" );
                $('#' + request_id).empty();
                $('#' + request_id).prepend('<button class="delete-alert" type="button">x</button>' +
                                            '<div class="alert-response-status">' + xhr.status + ' ' + textStatus + '</div>' +
                                            '<div class="alert-response-description">' +
                                                '<div class="id-of-tender"><span>Tender ID: </span><a href="' + tender_link + '" target="_blank">' + tender_id + '</a></div>' +
                                                '<div class="actual-tender-status"><span>Tender status: </span>' + tender_status + '</div>' +
                                                '<div class="operation-status"><span>Request status: </span>' + operation_status + '</div>' +
                                                '<div class="tender-to-company-status"><span>Add to company status: </span>' + tender_to_company_status + '</div>' +
                                            '</div>'
                //jsonPrettyPrint.toHtml(data)
                                            );
                //$('#createTender').removeAttr("disabled");
            },
            error: function (jqXHR) {
                //$("#created_tender_json").html(JSON.parse(jqXHR.responseText));
                //alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
				var error_description = JSON.parse(jqXHR.responseText).description
				var error_type = JSON.parse(jqXHR.responseText).error
                $('#' + request_id).addClass('response-content-error').toggleClass( "response-content-waiting" );
                $('#' + request_id).empty();
                $('#' + request_id).append('<button class="delete-alert" type="button">x</button>' + //jsonPrettyPrint.toHtml(JSON.parse(jqXHR.responseText)));
				'<div class="alert-response-status">' + error_type + '</div>' +
				'<div class="alert-response-description">' + error_description + '</div>'
				);
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
$(document).on("click",".delete-alert", function(){
    $(this).closest('div').remove();
});

