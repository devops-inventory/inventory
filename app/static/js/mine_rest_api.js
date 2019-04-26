$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#inventory_id").val(res.id);
        $("#inventory_id_inputted").val(res._id);
        $("#inventory_name").val(res.name);
        $("#inventory_category").val(res.category);
        $("#inventory_available").val(res.available);
        $("#inventory_condition").val(res.condition);
        $("#inventory_count").val(res.count);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#inventory_name").val("");
        $("#inventory_category").val("");
        $("#inventory_available").val("");
        $("#inventory_condition").val("");
        $("#inventory_count").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
      $("#flash_message").empty();
      $("#flash_message").append(message);
    }

    // ****************************************
    // Create a inventory
    // ****************************************

    $("#create-btn").click(function () {

        var name = $("#inventory_name").val();
        var category = $("#inventory_category").val();
        var available = $("#inventory_available").val();
        var condition = $("#inventory_condition").val();
        var count = $("#inventory_count").val();

        var data = {
            "name": name,
            "category": category,
            "available": available,
            "condition": condition,
            "count": count,
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/inventory",
            contentType:"application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a inventory
    // ****************************************

    $("#update-btn").click(function () {

        var inventory_id = $("#inventory_id").val();
        var name = $("#inventory_name").val();
        var category = $("#inventory_category").val();
        var available = $("#inventory_available").val();
        var condition = $("#inventory_condition").val();
        var count = $("#inventory_count").val();

        var data = {
            "name": name,
            "category": category,
            "available": available,
            "condition": condition,
            "count": count,
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/inventory/" + inventory.id,
                contentType:"application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
          update_form_data(res)
          flash_message("Success")
        });

        ajax.fail(function(res){
          flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a inventory
    // ****************************************

    $("#retrieve-btn").click(function () {

        var inventory_id = $("#inventory_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/inventory/" + inventory.id,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Inventory
    // ****************************************

    $("#delete-btn").click(function () {

        var inventory_id = $("#inventory_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/inventory/" + inventory.id,
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Inventory Deleted!")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        clear_form_data()
    });

    // ****************************************
    // Void an inventory
    // ****************************************

    $("#void-btn").click(function () {

        var ajax = $.ajax({
            type: "PUT",
            url: "/inventory/" + inventory.id + "/void",
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message("Error Voiding Inventory")
        });
    });

    // ****************************************
    // Search for a inventory
    // ****************************************

    $("#search-btn").click(function () {

        var name = $("#inventory_name").val();
        var category = $("#inventory_category").val();
        var available = $("#inventory_available").val();
        var condition = $("#inventory_condition").val();
        var count = $("#inventory_count").val();

        var queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += 'category=' + category
            }
        }
        if (available) {
            if (queryString.length > 0) {
                queryString += '&available=' + available
            } else {
                queryString += 'available=' + available
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/inventory?" + queryString,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped">');
            var header = '<tr>'
            header += '<th style=width:20>ID</th>'
            header += '<th style="width:10">Name</th>'
            header += '<th style="width:10">Category</th>'
            header += '<th style="width:10">Available</th>'
            header += '<th style="width:20">Condition</th>'
            header += '<th style="width:20">Count</th></tr>'
            $("#search_results").append(header);
            for(var i = 0; i < res.length; i++) {
                var inventory = res[i];
                var row = "<tr><td>"+inventory.id+"</td><td>"+inventory.name+"</td><td>"+inventory.category+"</td><td>"+inventory.available+"</td><td>"+inventory.condition+"</td><td>"+inventory.count+"</td></tr>";
                $("#search_results").append(row);
            }

            $("#search_results").append('</table>');
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
