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
        if(confirm("Are you sure you want to delete this tender?")){
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

//Delete auction
$(document).on("click",".auction-action-delete", function() {
        if(confirm("Are you sure you want to delete this auction?")){
            var id = $(this).attr('id');
            $.ajax({
                url: '/backend/jquery/auctions/' + id,
                type: 'DELETE',
                success: function() {
                    $('#auction-id-' + id).remove();
                },
                error: function (jqXHR, textStatus, errorThrown) {
                      getHtmlFromResponseError(jqXHR.responseText);
                }
            });
        }
        else {
            return false;
        }
});

//Delete user
$(document).on("click",".user-action-delete", function() {
        if(confirm("Are you sure you want to delete this user?")){
            var id = $(this).attr('id');
            $.ajax({
                url: '/backend/jquery/users/' + id,
                type: 'DELETE',
                success: function() {
                    $('#user-id-' + id).remove();
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

//Delete all tenders from DB
$(document).on("click","#delete-tenders", function() {
        if(confirm("Are you sure you want to delete all tenders?")){
            var id = $(this).attr('id');
            $.ajax({
                url: '/backend/jquery/tenders',
                type: 'DELETE',
                success: function() {
                    location.reload();
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


//Delete all auctions from DB
$(document).on("click","#delete-auctions", function() {
        if(confirm("Are you sure you want to delete all auctions?")){
            var id = $(this).attr('id');
            $.ajax({
                url: '/backend/jquery/auctions',
                type: 'DELETE',
                success: function() {
                    location.reload();
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


// Get HTML from alert ERROR
function getHtmlFromResponseError(value) {
	"use strict";
	var body;
	var html;
	body = JSON.parse(value).description
	html = $.parseHTML(body);
	$('#alertContainer').append(html);
	$('#alertContainer div:last-child').fadeIn(600);
    return html
};
