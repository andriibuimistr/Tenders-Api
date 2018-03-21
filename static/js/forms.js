//Generate random id
var randomString = function(length) {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for(var i = 0; i < length; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
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


//Add tender bid to company
$(document).on("click",".tender-bid-company-button", function() {
        $(this).prop('disabled', true);
        var bid  = $(this).closest("form").attr('id');
		var form = $(this).closest("form");
		var parent_div = $(this).closest(".bid-company");
        $.ajax({
            url: '/api/tenders/bids/' + bid + '/company',
            data: $(this).closest('form').serialize(),
            type: 'PATCH',
            success: function(data) {
                form.remove();
                parent_div.append(data);
                $('.tender-bid-company-button').removeAttr("disabled");
            },
            error: function (jqXHR, textStatus, errorThrown) {
            	alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                $('.tender-bid-company-button').removeAttr("disabled");
            }
        });
    });

//Add auction bid to company
$(document).on("click",".auction-bid-company-button", function() {
        $(this).prop('disabled', true);
        var bid  = $(this).closest("form").attr('id');
		var form = $(this).closest("form");
		var parent_div = $(this).closest(".bid-company");
        $.ajax({
            url: '/api/auctions/bids/' + bid + '/company',
            data: $(this).closest('form').serialize(),
            type: 'PATCH',
            success: function(data) {
                form.remove();
                parent_div.append(data);
                $('.auction-bid-company-button').removeAttr("disabled");
            },
            error: function (jqXHR, textStatus, errorThrown) {
            	alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                $('.auction-bid-company-button').removeAttr("disabled");
            }
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
                console.log(data)
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
                                                '<div class="actual-tender-status"><span>procurementMethodType: </span>' + procedure + '</div>' +
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


//Get list of bids for tender
$(function() {
    $('#get-tender-bids-button').click(function() {
        $(this).prop('disabled', true);
        var form = $("#get-tender-bids-form");
        var bid_id = $("#get-tender-bids-form input[name=tender_id]").val();
        $.ajax({
            url: '/api/tenders/' + bid_id + '/bids',
            crossDomain: true,
            type: 'GET',
            success: function(data, textStatus, xhr) {
                $('#list-of-bids').empty();
                $('#list-of-bids').append(data);
                $('#get-tender-bids-button').removeAttr("disabled");
            },
            error: function (jqXHR) {
				var error_description = JSON.parse(jqXHR.responseText).description
				var error_type = JSON.parse(jqXHR.responseText).error
                $('#list-of-bids').empty();
                $('#list-of-bids').append(jqXHR.responseText);
                $('#get-tender-bids-button').removeAttr("disabled");
            }
        });
    });
});


//Get list of bids for auction
$(function() {
    $('#get-auction-bids-button').click(function() {
        $(this).prop('disabled', true);
        var form = $("#get-auction-bids-form");
        var bid_id = $("#get-auction-bids-form input[name=auction_id]").val();
        $.ajax({
            url: '/api/auctions/' + bid_id + '/bids',
            crossDomain: true,
            type: 'GET',
            success: function(data, textStatus, xhr) {
                $('#list-of-bids').empty();
                $('#list-of-bids').append(data);
                $('#get-auction-bids-button').removeAttr("disabled");
            },
            error: function (jqXHR) {
				var error_description = JSON.parse(jqXHR.responseText).description
				var error_type = JSON.parse(jqXHR.responseText).error
                $('#list-of-bids').empty();
                $('#list-of-bids').append(jqXHR.responseText);
                $('#get-auction-bids-button').removeAttr("disabled");
            }
        });
    });
});

//ADMIN

//Add new platform
$(function() {
    $('.add-platform-button').click(function() {
        $(this).prop('disabled', true);
		var form = $(this).closest("form");
        $.ajax({
            url: '/backend/jquery/add_platform',
            data: $(this).closest('form').serialize(),
            type: 'POST',
            success: function(data) {
                $('#admin-list-of-platforms').append(data);
                $('.add-platform-button').removeAttr("disabled");
            },
            error: function (jqXHR, textStatus, errorThrown) {
            	alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                $('.add-platform-button').removeAttr("disabled");
            }
        });
    });
});

//Add new user
$(function() {
    $('.add-user-button').click(function() {
        $(this).prop('disabled', true);
        $.ajax({
            url: '/backend/jquery/add_user',
            data: $(this).closest('form').serialize(),
            type: 'POST',
            success: function(data) {
                $('#admin-list-of-users').append(data);
                $('.add-user-button').removeAttr("disabled");
            },
            error: function (jqXHR, textStatus, errorThrown) {
            	alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                $('.add-user-button').removeAttr("disabled");
            }
        });
    });
});

//Delete platform
$(document).on("click",".platform-action-delete", function() {
        if(confirm("Are you sure you want to delete this?")){
            var id = $(this).attr('id');
            $.ajax({
                url: '/backend/jquery/platforms/' + id,
                type: 'DELETE',
                success: function() {
                    $('#platform-id-' + id).remove();
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                }
            });
        }
        else {
            return false;
        }
});

//Delete tender
$(document).on("click",".tender-action-delete", function() {
        if(confirm("Are you sure you want to delete this?")){
            var id = $(this).attr('id');
            $.ajax({
                url: '/backend/jquery/tenders/' + id,
                type: 'DELETE',
                success: function() {
                    $('#tender-id-' + id).remove();
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                }
            });
        }
        else {
            return false;
        }
});

//Render JSON from form (input)
$(function() {
    $('#render_json_insert').click(function() {
        if(testJSON($('#raw_json_input').val()) === true){
			var raw_json = jQuery.parseJSON($('#raw_json_input').val());
			$("#json_output").jsonViewer(raw_json);
		}
		else {
			alert('Invalid JSON');
		}
    });
});

//Render JSON from CDB
$(function() {
    $('#render_json_get').click(function() {
        $(this).prop('disabled', true);
		var tender_id = $("#form-view-json-get input[name=tender_id_long]").val();
		var api_version = $("#form-view-json-get select[name=api_version]").val();
		$.ajax({
            url: '/backend/jquery/get_tender_json/' + tender_id + '/' + api_version,
            type: 'GET',
            success: function(data) {
                console.log(data);
                $("#json_output").jsonViewer(data);
				$('#render_json_get').removeAttr("disabled");
			},
            error: function (jqXHR, textStatus, errorThrown) {
            	alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                $('#render_json_get').removeAttr("disabled");
            }
        });
    });
});

//Test if is JSON
function testJSON(input){
    try{
        JSON.parse(input);
        return true;
    }
    catch (error){
        return false;
    }
}

//AUCTIONS
//Create auction
$(function() {
    $('#createAuction').click(function() {
        var form = $("#create-tender");
        var request_id = randomString(32);
        var procedure = $("#create-tender select[name=procurementMethodType]").val();
        var expected_status = $("#create-tender select[name=auctionStatus]").val();
        var html_for_wait = '<div class="alert-response-status">Waiting for response</div>' +
                            '<div class="alert-response-description">' +
                                '<div class="wait-procedure-type"><span>Procedure: </span>' + procedure + '</div>' +
                                '<div class="wait-tender-status"><span>Expected Auction Status: </span>' + expected_status + '</div>' +
                            '</div>'
                            ;
        $('#created_tender_json').prepend('<div class="response-content response-content-waiting" id="' + request_id + '">' + html_for_wait + '</div>');
        $.ajax({
            url: '/api/auctions',
            dataType : 'json',
            crossDomain: true,
            data: form.serialize(),
            type: 'POST',
            success: function(data, textStatus, xhr) {
                var operation_status = data.status;
                var tender_status = data.auctionStatus;
                var tender_to_company_status = data.tender_to_company[0].status;
                var tender_id = data.id;
                var tender_link = data.tender_to_company[1];
                $('#' + request_id).addClass('response-content-success').toggleClass( "response-content-waiting" );
                $('#' + request_id).empty();
                $('#' + request_id).prepend('<button class="delete-alert" type="button">x</button>' +
                                            '<div class="alert-response-status">' + xhr.status + ' ' + textStatus + '</div>' +
                                            '<div class="alert-response-description">' +
                                                '<div class="id-of-tender"><span>Auction ID: </span><a href="' + tender_link + '" target="_blank">' + tender_id + '</a></div>' +
                                                '<div class="actual-tender-status"><span>Auction status: </span>' + tender_status + '</div>' +
                                                '<div class="operation-status"><span>Request status: </span>' + operation_status + '</div>' +
                                                '<div class="tender-to-company-status"><span>Add to company status: </span>' + tender_to_company_status + '</div>' +
                                            '</div>'
                                            );
            },
            error: function (jqXHR) {
				var error_description = JSON.parse(jqXHR.responseText).description;
				var error_type = JSON.parse(jqXHR.responseText).error;
                $('#' + request_id).addClass('response-content-error').toggleClass( "response-content-waiting" );
                $('#' + request_id).empty();
                $('#' + request_id).append('<button class="delete-alert" type="button">x</button>' +
				'<div class="alert-response-status">' + error_type + '</div>' +
				'<div class="alert-response-description">' + error_description + '</div>'
				);
            }
        });
    });
});


//Disable unnecessary forms on auction creation page
$(function() {
    var disable_select = function () {
        if ($("#cdb_version").val() === '2') {
            $("#procurementMethodType").val('dgfOtherAssets');  // Disable procurementMethodType select for cdb2
			$('#procurementMethodType option[value="dgfFinancialAssets"]').prop('disabled', 'disabled');
			$('#procurementMethodType option[value="dgfInsider"]').prop('disabled', 'disabled');
			$("#steps").prop('disabled', 'disabled').val('80');
            $("#rent").prop('disabled', false);
            $("#skip_auction").prop('disabled', 'disabled').prop('checked', false);
			$('#rent').change(function(){
				   $("#minNumberOfQualifiedBids").prop("disabled", !$(this).is(':checked'));
				   $("#minNumberOfQualifiedBids").prop('checked', false, !$(this).is(':checked'));
				});
        }
        else {
            $('#procurementMethodType option[value="dgfFinancialAssets"]').prop('disabled', false);
            $('#procurementMethodType option[value="dgfInsider"]').prop('disabled', false);
            $("#minNumberOfQualifiedBids").prop('disabled', 'disabled').prop('checked', false);
            $("#rent").prop('disabled', 'disabled').prop('checked', false);
            $("#skip_auction").prop('disabled', false)
			var disable_steps = function (){
				        if ($("#procurementMethodType").val() === 'dgfInsider') {
							$("#steps").prop('disabled', false);
						}
						else {
							$("#steps").prop('disabled', 'disabled').val('80');
						}
			};
			$(disable_steps);
			$("#procurementMethodType").change(disable_steps);
        }
      };
      $(disable_select);
      $("#cdb_version").change(disable_select);
});


//Disable features checkbox on tender creation page
$(function() {
    var disable_select = function () {
        no_features = ['negotiation.quick', 'negotiation', 'reporting'];
        if (jQuery.inArray($("#procurementMethodType").val(), no_features)!='-1') {
            $("#if_features").prop('disabled', true).prop('checked', false);
            $("#skip_tender_auction").prop('disabled', true).prop('checked', false);
        }
        else {
            $("#if_features").prop('disabled', false);
            $("#skip_tender_auction").prop('disabled', false).prop('checked', true);
        }
      };
      $(disable_select);
      $("#procurementMethodType").change(disable_select);
});


$(function() {
    var disable_select = function () {
        var limited = ['negotiation.quick', 'negotiation', 'reporting'];
		var above = [];
		var prequalification = ['esco', 'aboveThresholdEU', 'competitiveDialogueEU', 'competitiveDialogueUA'];
        var status_limited = "active,complete,active.award,active.contract";
        var competitive = ['competitiveDialogueEU', 'competitiveDialogueUA'];
        var status_non_limited = "active.tendering,active.tendering.stage2,active.pre-qualification,active.pre-qualification.stage2,active.pre-qualification.stage2,active.qualification,active.enquiries";
        if (jQuery.inArray($("#procurementMethodType").val(), limited)=='-1') { //if is not limited block limited statuses
                    $.each(status_limited.split(","), function(i,e){   //disable limited statuses for above procedures
                        $("#tenderStatus option[value='" + e + "']").prop('disabled', true);
                    });
                    $.each(status_non_limited.split(","), function(i,e){  //enable above statuses for above procedures
                        $("#tenderStatus option[value='" + e + "']").prop('disabled', false);
                    });
                    $('#tenderStatus').children('option:enabled').eq(0).prop('selected',true);  //select first enabled element
                    var disable_enquiry = function (){
				        if ($("#procurementMethodType").val() !== 'belowThreshold') {
							$('#tenderStatus option[value="active.enquiries"]').prop('disabled', true);
						}
						else {
							$('#tenderStatus option[value="active.enquiries"]').prop('disabled', false);
						}
                    };
                    $(disable_enquiry);
                    var disable_2nd_preq = function (){
				        if ($("#procurementMethodType").val() !== 'competitiveDialogueEU') {
							$('#tenderStatus option[value="active.pre-qualification.stage2"]').prop('disabled', true);
						}
						else {
							$('#tenderStatus option[value="active.pre-qualification.stage2"]').prop('disabled', false);
						}
                    };
                    $(disable_2nd_preq);
                    var disable_competitive = function (){
				        if (jQuery.inArray($("#procurementMethodType").val(), competitive)=='-1') {
							$('#tenderStatus option[value="active.tendering.stage2"]').prop('disabled', true);
						}
						else {
							$('#tenderStatus option[value="active.tendering.stage2"]').prop('disabled', false);
						}
                    };
                    $(disable_competitive);
                    var disable_preq = function (){
				        if (jQuery.inArray($("#procurementMethodType").val(), prequalification)=='-1') {
							$('#tenderStatus option[value="active.pre-qualification"]').prop('disabled', true);
						}
						else {
							$('#tenderStatus option[value="active.pre-qualification"]').prop('disabled', false);
						}
                    };
                    $(disable_preq);
        }
        else if(jQuery.inArray($("#procurementMethodType").val(), above)=='-1'){ //if is not above procedure
                       $.each(status_non_limited.split(","), function(i,e){  //disable above statuses for not above procedures
                        $("#tenderStatus option[value='" + e + "']").prop('disabled', true);
                    });
                    $.each(status_limited.split(","), function(i,e){  //enable limited statuses for limited procedures
                        $("#tenderStatus option[value='" + e + "']").prop('disabled', false);
                    });
                    $('#tenderStatus').children('option:enabled').eq(0).prop('selected',true);  //select first enabled element
					var disable_lots_reporting = function (){
				        if ($("#procurementMethodType").val() === 'reporting') {
							$('#number_of_lots').prop('disabled', true).val('');
						}
						else {
							$('#number_of_lots').prop('disabled', false);
						}
                    };
                    $(disable_lots_reporting);
					$("#procurementMethodType").change(disable_lots_reporting);
        }
        else {
                    $.each(status_limited + status_non_limited.split(","), function(i,e){
                        $("#tenderStatus option[value='" + e + "']").prop('disabled', false);
                    });
        }
      };
      $(disable_select);
      $("#procurementMethodType").change(disable_select);
});