
//Clear created tender response json
$(function() {
    $('#clear-createTender-response').click(function() {
        $("#created_tender_json").empty();
    });
});


//Clear created tender response json
$(function() {
    $('#clear-createMonitoring-response').click(function() {
        $("#created_monitoring_json").empty();
    });
});


//Delete alert in "console"
$(document).on("click",".delete-alert", function(){
    $(this).closest('div').remove();
});



//Disable unnecessary inputs on auction creation page
$(function() {
    var disable_select = function () {
        if ($("#cdb_version").val() === '2') {
            $('#procurementMethodType option[value="propertyLease"]').prop('disabled', false);  // enable propertyLease for cdb 2
            $("#procurementMethodType").val('dgfOtherAssets');  // Disable procurementMethodType select for cdb2
			$('#procurementMethodType option[value="dgfFinancialAssets"]').prop('disabled', 'disabled');
			$('#procurementMethodType option[value="dgfInsider"]').prop('disabled', 'disabled');
			$("#steps").prop('disabled', 'disabled').val('80');
            $("#rent").prop('disabled', false);
			$('#rent').change(function(){
				   $("#minNumberOfQualifiedBids").prop("disabled", !$(this).is(':checked'));
				   $("#minNumberOfQualifiedBids").prop('checked', false, !$(this).is(':checked'));
				});
        }
        else {
            $('#procurementMethodType option[value="propertyLease"]').prop('disabled', 'disabled');  // disable propertyLease for cdb 1
            $('#procurementMethodType option[value="dgfFinancialAssets"]').prop('disabled', false);
            $('#procurementMethodType option[value="dgfInsider"]').prop('disabled', false);
            $("#minNumberOfQualifiedBids").prop('disabled', 'disabled').prop('checked', false);
            $("#rent").prop('disabled', 'disabled').prop('checked', false);
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


//Disable options for limited procedures on tender creation page
$(function() {
    var disable_select = function () {
        limited = ['negotiation.quick', 'negotiation', 'reporting'];
        if (jQuery.inArray($("#procurementMethodType").val(), limited)!='-1') {
            $("#if_features").prop('disabled', true).prop('checked', false);
            $("#skip_tender_auction").prop('disabled', true).prop('checked', false);
            $("#docs_for_bids").prop('disabled', true)
            $('#numberOfBids').prop('disabled', true);
        }
        else {
            $("#if_features").prop('disabled', false);
            $("#skip_tender_auction").prop('disabled', false).prop('checked', true);
            $("#docs_for_bids").prop('disabled', false)
            $('#numberOfBids').prop('disabled', false);
        }
      };
      $(disable_select);
      $("#procurementMethodType").change(disable_select);
});

//Disable unnecessary inputs on tender creation page
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
							$('#tenderStatus option[value="complete"]').prop('disabled', true);
						}
						else {
							$('#tenderStatus option[value="active.tendering.stage2"]').prop('disabled', false);
							$('#tenderStatus option[value="complete"]').prop('disabled', false);
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
					var disable_lots_reporting = function (){
				        if ($("#procurementMethodType").val() === 'reporting') {
							$('#numberOfLots').prop('disabled', true);
						}
						else {
							$('#numberOfLots').prop('disabled', false);
						}
                    };
                    $(disable_lots_reporting);
					$("#procurementMethodType").change(disable_lots_reporting);
        }
        else {
                    $.each(status_limited + status_non_limited.split(","), function(i,e){
                        $("#tenderStatus option[value='" + e + "']").prop('disabled', false);
                    });
        };
        if ($('#tenderStatus option:selected').is(':disabled')){  // select first enabled option only if current option is disabled
            $('#tenderStatus').children('option:enabled').eq(0).prop('selected',true);  //select first enabled element
            console.log('select was changed!')
        }
      };

      $(disable_select);
      $("#procurementMethodType").change(disable_select);
});

// Delete invalid class if input "number of lots" is disabled
$(function() {
    var delete_class = function () {
        if ($('#numberOfLots').is(':disabled')) {
            $('#numberOfLots').removeClass('input-invalid');
        }
//        else {
//            $('#numberOfLots').addClass('input-invalid');
//        }
        if ($('#numberOfBids').is(':disabled')) {
            $('#numberOfBids').removeClass('input-invalid');
        }
//        else {
//            $('#numberOfBids').addClass('input-invalid');
//        }
      };
      $(delete_class);
      $("#procurementMethodType").change(delete_class);
});

//Disable unnecessary inputs on monitoring creation page
$(function() {
	$('#showTenderIdInput').prop('checked', true);
    var disable_input = function () {
        if ($('#showTenderIdInput').is(':checked')) {  // If is checked
            $("#tender_id_long").prop('disabled', true);
            $("#company_id").prop('disabled', false);
			$('#monitoringStatus option[value="completed"]').prop('disabled', false);
        }
        else {
            $("#tender_id_long").prop('disabled', false);
            $("#company_id").prop('disabled', true);
			$('#monitoringStatus option[value="completed"]').prop('disabled', true);
			if ($('#company_id').is(':disabled')) {
                $('#company_id').removeClass('input-invalid');
            }
        }
		
		if ($('#monitoringStatus option:selected').is(':disabled')){  // select first enabled option only if current option is disabled
		$('#monitoringStatus').children('option:enabled').eq(0).prop('selected',true);  //select first enabled element
		console.log('select was changed!');
        }
      };
      $(disable_input);
      $("#showTenderIdInput").change(disable_input);
});

// MODAL WINDOWS
// Open modal window for add new report
$(document).on("click","#bugReport", function(){
	if ($('.modal-bug-report').length){
		$('.modal-bug-report').show();
	}
	else{
	$('#modalWindowContainer').empty();
	$.ajax({
		url: '/modal/add_report',
		type: 'get',
		success: function(data){
			$('#modalWindowContainer').append(data);
			$('.modal-bug-report').show();
		},
		error: function (jqXHR, textStatus, errorThrown) {
			alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
		}
	});
	}
});

// Open modal window for edit report
$(document).on("click","#editReportButton", function(){
	if ($('.modal-bug-report').length){
		$('.modal-bug-report').show();
	}
	else{
    var report_id = $('#reportId').val()
	$('#modalWindowContainer').empty();
	$.ajax({
		url: '/modal/edit_report/' + report_id,
		type: 'GET',
		success: function(data){
			$('#modalWindowContainer').append(data);
			$('.modal-bug-report').show();
		},
		error: function (jqXHR, textStatus, errorThrown) {
			alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
		}
	});
	}
});

// Close modal window
$(document).on("click","#closeModal", function(){
	$('.modal-bug-report').hide();
	$('#modalWindowContainer').empty();
});

// Close modal window and reload page
$(document).on("click",".doReload", function(){
	$('.modal-bug-report').hide();
	$('#modalWindowContainer').empty();
	location.reload();
});


// Convert text into html
function parseTextToHtml(locator) {
	"use strict";
	var str;
	var html;
    str = locator.text();
	html = $.parseHTML(str);
	locator.empty();
	locator.append(html);
}

// Convert content (text) of report into html
$( document ).ready(function() {
	"use strict";
	parseTextToHtml($('.report-view-content'));
});