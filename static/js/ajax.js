
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
        var inputsRequired = [$('#numberOfItems'), $('#accelerator'), $('#companyId')]; // List of required inputs
        var inputsInteger = [$('#numberOfLots'), $('#numberOfItems'), $('#accelerator'), $('#companyId'), $('#numberOfBids')]; // List of Integer inputs
        if (!validateInputs(inputsRequired)){
            return false;
            }
        else if (!validateInputsInteger(inputsInteger)){
            return false;
            }
        else {
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
        };
    });
});

//Add tender bid to company
$(document).on("click",".tender-bid-company-button", function() {
        var button = $(this).prop('disabled', true);
        button = button.prop('disabled', true);
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
                button.removeAttr("disabled");
            },
            error: function (jqXHR, textStatus, errorThrown) {
            	getHtmlFromResponseError(jqXHR.responseText);
                button.removeAttr("disabled");
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
				getHtmlFromResponseError(jqXHR.responseText);
                $('#get-tender-bids-button').removeAttr("disabled");
            }
        });
    });
});


//AUCTIONS
//Create auction
$(function() {
    $('#createAuction').click(function() {
        var inputsRequired = [$('#numberOfItems'), $('#accelerator'), $('#companyId')]; // List of required inputs
        var inputsInteger = [$('#numberOfItems'), $('#accelerator'), $('#companyId'), $('#numberOfBids')]; // List of Integer inputs
        if (!validateInputs(inputsRequired)){
            return false;
            }
        else if (!validateInputsInteger(inputsInteger)){
            return false;
            }
		else {
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
        };
    });
});


//Create privatization
$(function() {
    $('#createAuctionPrivatization').click(function() {
        var inputsRequired = [$('#numberOfItems'), $('#numberOfBids'), $('#acceleratorAsset'), $('#acceleratorLot'), $('#accelerator'), $('#companyId')]; // List of required inputs
        if (!validateInputs(inputsRequired)){
            return false;
            }
        else if (!validateInputsInteger(inputsRequired)){  // all required inputs are integer
            return false;
            }
		else {
            var form = $("#create-tender");
            var request_id = randomString(32);
            var expected_status = $("#create-tender select[name=auctionStatus]").val();
            var html_for_wait = '<div class="alert-response-status">Waiting for response</div>' +
                                '<div class="alert-response-description">' +
                                    '<div class="wait-tender-status"><span>Expected Auction Status: </span>' + expected_status + '</div>' +
                                '</div>'
                                ;
            $('#created_tender_json').prepend('<div class="response-content response-content-waiting" id="' + request_id + '">' + html_for_wait + '</div>');
            $.ajax({
                url: '/api/privatization',
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
        };
    });
});

//Add auction bid to company
$(document).on("click",".auction-bid-company-button", function() {
        var button = $(this).prop('disabled', true);
        button = button.prop('disabled', true);
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
                button.removeAttr("disabled");
            },
            error: function (jqXHR, textStatus, errorThrown) {
            	getHtmlFromResponseError(jqXHR.responseText);
                button.removeAttr("disabled");
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
				getHtmlFromResponseError(jqXHR.responseText);
                $('#get-auction-bids-button').removeAttr("disabled");
            }
        });
    });
});

//Create Monitoring
$(function() {
    $('#createMonitoring').click(function() {
		var inputsRequired = [$('#accelerator'), $('#company_id'), $('#tender_id_long')]; // List of required inputs
		var inputsInteger = [$('#accelerator'), $('#company_id')]; // List of int inputs
        if (!validateInputs(inputsRequired)){
            return false;
            }
        else if (!validateInputsInteger(inputsInteger)){
            return false;
            }
		else {
			var form = $("#create-monitoring");
			var request_id = randomString(32);
			var procedure = $("#create-monitoring select[name=procurementMethodType]").val();
			var expected_status = $("#create-monitoring select[name=monitoringStatus]").val();
			var html_for_wait = '<div class="alert-response-status">Waiting for response</div>' +
								'<div class="alert-response-description">' +
									'<div class="wait-procedure-type"><span>Procedure: </span>' + procedure + '</div>' +
									'<div class="wait-tender-status"><span>Expected Monitoring Status: </span>' + expected_status + '</div>' +
								'</div>'
								;
			$('#created_monitoring_json').prepend('<div class="response-content response-content-waiting" id="' + request_id + '">' + html_for_wait + '</div>');
			$.ajax({
				url: '/api/monitorings',
				dataType : 'json',
				crossDomain: true,
				data: form.serialize(),
				type: 'POST',
				success: function(data, textStatus, xhr) {
					console.log(data);
//					var operation_status = data.status;
					var monitoring_status = data.monitoringStatus;
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
													'<div class="actual-tender-status"><span>Monitoring status: </span>' + monitoring_status + '</div>' +
	//                                                '<div class="operation-status"><span>Request status: </span>' + operation_status + '</div>' +
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
		};
    });
});


// Submit "Add new report form"
$(document).on("click","#addReportButton", function(){
        var inputs = [$('#reportTitle'), $('#reportContent')]; // List of required inputs
        if (!validateInputs(inputs)){
            console.log('BAD')
            if ($('#reportContent').hasClass('input-invalid')) {
                $('.note-editor').addClass('input-invalid')
            }
            return false
        }
        else {
            var filesNumber = $('.form-control-file').length;  // Get number of files inputs
            var fd = new FormData();
            for (i = 0; i < filesNumber; i++) {
                fd.append('file' + i, $("input[id='UploadedFile[" + i + "][file]']")[0].files[0]); // Append every file to FormData
            }
            var listOfInputs = JSON.parse(JSON.stringify($('#addReportForm').serializeArray()));  // Convert inputs into json {'name': 'value'}
            for (i = 0; i < listOfInputs.length; i++){
                var inputName = listOfInputs[i]['name'];
                var inputValue = listOfInputs[i]['value'];
                fd.append(inputName, inputValue); // Append every input to FormData
            }
            $.ajax({
                url: '/modal/add_report',
                type: 'post',
                data: fd,
                contentType: false,
                processData: false,
                success: function(data){
                    $('.modal-body').empty();
                    $('.modal-body').append(data);
                    $('.modal-footer').remove();
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                }
            });
        }
    });

// Submit "Save edited report form"
$(document).on("click","#saveReportButton", function(){
        var inputs = [$('#reportTitle'), $('#reportContent')]; // List of required inputs
        if (!validateInputs(inputs)){
            if ($('#reportContent').hasClass('input-invalid')) {
                $('.note-editor').addClass('input-invalid')
            }
            return false
        }
        else {
            var report_id =  $('#reportId').val()
            var filesNumber = $('.form-control-file').length;  // Get number of files inputs
            var fd = new FormData();
            for (i = 0; i < filesNumber; i++) {
                fd.append('file' + i, $("input[id='UploadedFile[" + i + "][file]']")[0].files[0]); // Append every file to FormData
            }
            var listOfInputs = JSON.parse(JSON.stringify($('#editReportForm').serializeArray()));  // Convert inputs into json {'name': 'value'}
            for (i = 0; i < listOfInputs.length; i++){
                var inputName = listOfInputs[i]['name'];
                var inputValue = listOfInputs[i]['value'];
                fd.append(inputName, inputValue); // Append every input to FormData
            }
            $.ajax({
                url: '/modal/edit_report/' + report_id,
                type: 'patch',
                data: fd,
                contentType: false,
                processData: false,
                success: function(data){
                    $('.modal-body').empty();
                    $('.modal-body').append(data);
                    $('.modal-footer').remove();
                    $('.close').addClass('doReload')
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                }
            });
        }
    });

// Add file input to report
$(document).on("click","#addReportFileInput", function() {
    var filesInputsNumber = $('.form-control-file').length;  // Get number of files inputs
    $('#reportFiles').append('<input name="UploadedFile[' + filesInputsNumber +
    '][file]" type="file" class="form-control-file" id="UploadedFile[' + filesInputsNumber + '][file]">');
});

//Delete file from report
$(document).on("click",".report-document-action-delete", function() {
        if(confirm("Are you sure you want to delete this document?")){
            var id = $(this).attr('id');
            $.ajax({
                url: '/backend/jquery/report/files/' + id,
                type: 'DELETE',
                success: function() {
                    $('#document-id-' + id).remove();
                    $('.close').addClass('doReload')
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

// Validate if all inputs from list are filled
function validateInputs(list){
        var status = true
        for (i = 0; i < list.length; i++){
            if (list[i].val().trim() === "" && list[i].is(":not(:disabled)")) {
                list[i].addClass('input-invalid');
//                list[i].focus();
                var status = false;
            }
        }
//        if (!status){
//            alert("Please fill required fields");
//        }
        return status
}

$(document).on("blur", '.class-required', function() {
  if ($(this).val().trim() === "") { // not email
   $(this).addClass('input-invalid');
  }
});

$(document).on("focus", '.class-required', function() {
  if ($(this).val().trim() === "") { // not email
   $(this).removeClass('input-invalid');
  }
});

// Validate if all inputs from list are integer
function validateInputsInteger(list){
        var status = true
        for (i = 0; i < list.length; i++){
                if ((isNaN(list[i].val().trim()) && list[i].val().trim().length > 0 && list[i].is(':enabled')) || list[i].val().includes('.') && list[i].is(':enabled')) {
                    list[i].addClass('input-invalid');
                    var status = false;
                }
            }
        return status
}
