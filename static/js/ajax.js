
//Generate random id
var randomString = function(length) {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for(var i = 0; i < length; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}

//Create tender
$(function() {
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
                                            );
            },
            error: function (jqXHR) {
				var error_description = JSON.parse(jqXHR.responseText).description
				var error_type = JSON.parse(jqXHR.responseText).error
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

//Add tender to company
//$(function() {
//    $('.tender-company-button').click(function() {
//        $(this).prop('disabled', true);
//        var tid  = $(this).closest("form").attr('id');
//		var form = $(this).closest("form");
//        $.ajax({
//            url: '/tenders/' + tid + '/company',
//            data: $(this).closest('form').serialize(),
//            type: 'POST',
//            success: function(data) {
//                form.parent().html(data);
//                $('.tender-company-button').removeAttr("disabled");
//            },
//            error: function (jqXHR, textStatus, errorThrown) {
//            	alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
//                $('.tender-company-button').removeAttr("disabled");
//            }
//        });
//    });
//});

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
                $(this).prop('disabled', false);
            },
            error: function (jqXHR, textStatus, errorThrown) {
            	alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                $(this).prop('disabled', false);
            }
    });
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
                $(this).prop('disabled', false);
            },
            error: function (jqXHR, textStatus, errorThrown) {
            	alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                $(this).prop('disabled', false);
            }
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

