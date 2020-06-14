
$('#get-identity-btn').on('click', function(e) {
        $.ajax({
            url: "/api/identity/",
            type: 'GET',
            headers: {
                "X-CSRFToken": '{{ csrf_token }}'
            },
        })


            .done(function(data) {
                $('#get-identity-data').slideUp(function() {
                    if (data.error != null) {
                        displayError(this, data.error);
                        return;
                    }
                    var identityData = data.identity.accounts;
                    console.log(identityData);
                    var html = '<tr class="response-row response-row--is-identity"><td><strong>Names</strong></td><td><strong>Emails</strong></td><td><strong>Phone numbers</strong></td><td><strong>Addresses</strong></td></tr><tr class="response-row response-row--is-identity">';
                    html += '<td>';
                    identityData.names.forEach(function(name, idx) {
                        html += name + '<br />';
                    });
                    html += '</td><td>';
                    identityData.emails.forEach(function(email, idx) {
                        html += email.data + '<br />';
                    });
                    html += '</td><td>';
                    identityData.phone_numbers.forEach(function(number, idx) {
                        html += number.data + '<br />';
                    });
                    html += '</td><td>';
                    identityData.addresses.forEach(function(address, idx) {
                        html += address.data.street + '<br />';
                        html += address.data.city + ', ' + address.data.state + ' ' + address.data.zip;
                    });
                    html += '</td></tr>';
                    $(this).html(html).slideDown();
                });



            });
    });



    $('#get-balance-btn').on('click', function(e) {
        $.ajax({
            url: "/api/balance/",
            type: 'GET',
            headers: {
                "X-CSRFToken": '{{ csrf_token }}'
            },
        })
            .done(function(data) {
                $('#get-balance-data').slideUp(function() {
                    if (data.error != null) {
                        displayError(this, data.error);
                        return;
                    }
                    var balanceData = data.balance;
                    var html = '<tr><td><strong>Name</strong></td><td><strong>Balance</strong></td><td><strong>Subtype</strong></td><td><strong>Mask</strong></td></tr>';
                    balanceData.accounts.forEach(function(account, idx) {
                        html += '<tr>';
                        html += '<td>' + account.name + '</td>';
                        html += '<td>$' + (account.balances.available != null ? account.balances.available : account.balances.current) + '</td>'
                        html += '<td>' + account.subtype + '</td>';
                        html += '<td>' + account.mask + '</td>';
                        html += '</tr>';
                    });

                    $(this).html(html).slideDown();
                });
            });

    });


    $('#get-item-btn').on('click', function(e) {
        $.ajax({
            url: "/api/item/",
            type: 'GET',
            headers: {
                "X-CSRFToken": '{{ csrf_token }}'
            },
        })

            .done(function(data) {
                $('#get-item-data').slideUp(function() {
                    if (data.error) {
                        displayError(this, data.error);
                    } else {
                        var html = '';
                        html += '<tr><td>Institution name</td><td>' + data.institution.name + '</td></tr>';
                        html += '<tr><td>Billed products</td><td>' + data.item.billed_products.join(', ') + '</td></tr>';
                        html += '<tr><td>Available products</td><td>' + data.item.available_products.join(', ') + '</td></tr>';

                        $(this).html(html).slideDown();
                    }
                });


            });

    });

    $('#get-accounts-btn').on('click', function(e) {
        $.ajax({
            url: "/api/accounts/",
            type: 'GET',
            headers: {
                "X-CSRFToken": '{{ csrf_token }}'
            },
        })

            .done(function(data) {
                $('#get-accounts-data').slideUp(function() {
                    if (data.error != null) {
                        displayError(this, data.error);
                        return;
                    }
                    var accountData = data.balance;
                    console.log(accountData);
                    var html = '<tr><td><strong>Name</strong></td><td><strong>Balances</strong></td><td><strong>Subtype</strong></td><td><strong>Mask</strong></td></tr>';
                    accountData.accounts.forEach(function(account, idx) {
                        html += '<tr>';
                        html += '<td>' + account.name + '</td>';
                        html += '<td>$' + (account.balances.available != null ? account.balances.available : account.balances.current) + '</td>';
                        html += '<td>' + account.subtype + '</td>';
                        html += '<td>' + account.mask + '</td>';
                        html += '</tr>';
                    });

                    $(this).html(html).slideDown();
                });


            });

    });
