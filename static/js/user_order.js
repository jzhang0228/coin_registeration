(function() {
    var form_index = 1;
    function replaceAttr(element, attribute, index) {
        element.attr(attribute, element.attr(attribute).replace(0, index));
    }
    $(document).ready(function () {
        $('#add_order').click(function(event) {
            var $copiedForm = $("#origin_order_form").clone();
            var $input;
            event.preventDefault();
            $copiedForm.removeAttr('id');
            $.each($copiedForm.find('input'), function(index, input) {
                $input = $(input);
                replaceAttr($input, 'id', form_index);
                replaceAttr($input, 'name', form_index);
                $input.val('');
            });
            $.each($copiedForm.find('label'), function(index, label) {
                replaceAttr($(label), 'for', form_index);
            });
            $copiedForm.appendTo(".order_form");
            form_index++;
            $('#id_form-TOTAL_FORMS').val(form_index);
        });

        $(document).on('click', '.delete_order', function(event) {
            event.preventDefault();
            $(this).parent('.one_order').remove();
        })

        .on('click', '.pay-button', function(event) {
            var $payButton = $(this);
            var $payInput = $(this).siblings('.pay-input');
            var $tableRow = $(this).parents('tr');
            if ($payInput.hasClass('hide')) {
                $payInput.removeClass('hide');
            } else {
                $.ajax({
                    url: '../../pay_user/',
                    data: {
                        user_id: $(this).attr('data-id'),
                        amount: $payInput.val()
                    },
                    success: function(responseData) {
                        if (responseData.success) {
                            $tableRow.find('.paid-amount').html(responseData.paid_amount);
                            $tableRow.find('.unpaid-amount').html(responseData.unpaid_amount);
                            $tableRow.find('.due-amount').html(responseData.due_amount);
                            if (responseData.unpaid_amount <= 0) {
                                $payButton.hide();
                            }
                        }
                    }
                });
                $payInput.addClass('hide');
            }
        });
    })
})();