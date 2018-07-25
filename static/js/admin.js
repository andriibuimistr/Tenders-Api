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