function getDate(today) {
    var dd = today.getDate();
    var mm = today.getMonth()+1; //January is 0!

    var yyyy = today.getFullYear();
    if(dd<10){
        dd='0'+dd;
    }
    if(mm<10){
        mm='0'+mm;
    }
    return mm+'/'+dd+'/'+yyyy;
}

window.onload = function () {
    CanvasJS.addColorSet("custom", ["#44ffcd", "#FFFFFF"]);

    var uid = $('#uid');
    // var info = make_request
    
    var loans_taken = parseFloat($('#loan_taken').html());
    var diff = parseFloat($('#loan_limit').html()) - loans_taken;

    var chart = new CanvasJS.Chart("chartContainer", {
        colorSet:  "custom",
        animationEnabled: true,
        interactivityEnabled: false,
        backgroundColor: null,
        title:null,
        data: [{
            type: "doughnut",
            startAngle: 90,
            innerRadius: 120,
            dataPoints: [
                { y: diff },
                { y: loans_taken }
            ]
        }]
    });
    chart.render();
    $('.canvasjs-chart-credit').remove();
    $('.canvasjs-chart-tooltip').remove();
    $('.canvasjs-chart-container').css('position', 'absolute');
    var height = $('.canvasjs-chart-canvas').css('height');
    var width = $('.canvasjs-chart-canvas').css('width');
    var element = "<div class=\"center-message\"><h1>$" + diff + "</h1>Loanable Funds <br>Available</div>"
    var center_elem = 
        "<div class=\"container flex-center\" style=\"align-items: center; justify-content: center; height:" + height + "; width:" + width + "\">" + element + "</div>";
    $('.canvasjs-chart-container').append(center_elem);

    var today = new Date();
    today.setMonth(today.getMonth() + 1)
    onemonth = '<p id="one_month_due_date">Due: ' + getDate(today) + '</p>';
    onemonth += '<p>Amount Due: $<span id=\"one_month_due\">' + '0.00' + '</span></p>';  

    today.setMonth(today.getMonth() + 1)
    twomonth = '<p id="two_month_due_date">Due: ' + getDate(today)+ '</p>';
    twomonth += '<p>Amount Due: $<span id=\"two_month_due\">' + '0.00' + '</span></p>';  

    today.setMonth(today.getMonth() + 1)
    threemonth = '<p id="three_month_due_date">Due: ' + getDate(today)+'</p>';
    threemonth += '<p>Amount Due: $<span id=\"three_month_due\">' + '0.00' + '</span></p>';  

    $('#one_month_modal').html($('#one_month_modal').html() + onemonth);
    $('#two_month_modal').html($('#two_month_modal').html() + twomonth);
    $('#three_month_modal').html($('#three_month_modal').html() + threemonth);
}

$(document).ready(function() {
    $('.opt-but').click(function() {
        if ($(this).hasClass('active-btn')) {
            return;
        }

        var curr_active = $('.active-btn.opt-but');
        var next_active = $(this);

        $.when($(curr_active).removeClass('active-btn'))
        .then($("#" + $(curr_active).attr('id') + "_modal").addClass('opc'))
        .then($("#" + $(next_active).attr('id') + "_modal").removeClass('opc'))
        .done(function() {$(next_active).addClass('active-btn')});
    });

    $('#loan_value').change(function() {
        var val = parseInt($('#loan_value').val())
        $('#one_month_due').html(( val * 1.1 ).toFixed(2));
        $('#two_month_due').html(( val * 1.15 ).toFixed(2));
        $('#three_month_due').html(( val * 1.2 ).toFixed(2));
    });

});

