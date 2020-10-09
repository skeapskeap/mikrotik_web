$(document).ready(function (){ //метод jQuery ready() начинает работать когда готов DOM, медиа-контент может загружаться позже
    
    function getCookie(name) { //функция парсит document.cookie по аргументу (name='csrftoken') и возвращает значение токена
        var cookieValue = null;

        if (document.cookie && document.cookie !=='') {
            var cookie = document.cookie.split(';');                            //cookie это строка из элементов с ключами и разделителем ';'

            for (var i = 0; i < cookie.length; i++) {                           //проход по списку нарезанному из cookies
                var cookie = cookie[i].trim();                                  //trim аналог strip в python

                if (cookie.substring(0, name.length + 1) === (name + '=')) {    //если найден элемент с ключем (name)
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    var csrfToken = getCookie('csrftoken'); //присваивает в переменную csrfToken результат функции getCookie

    function csrfSafeMethod(method) {       //функция возвращает true для методов !='POST'
        return ['GET', 'OPTIONS', 'HEAD', 'TRACE'].includes(method);
    }

    $.ajaxSetup({                           //функция запихивает csrfToken в http header потому что так круче, чем передавать его внутри POST
        beforeSend: function(xhr, setting) {
            if (!csrfSafeMethod(setting.type) && !this.crossDomain) { //setting.type возвращает метод, в нашем случае POST
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }     
        }
    });

    function displayResponse(response) {
        if (response.error) {               // if there is validation error in form
            $('#check_result').empty()
            $('#error').text(response.error)
        }

        else {                              // if validation passed
            $('#error').empty()
            var pathname = window.location.pathname; // Returns path only (/path/example.html)
            var arp = response.arp
            var dhcp = response.dhcp
            var acl = response.acl
            var message = response.message
            
            if (pathname === '/') {
                $('#check_result').text(message)  // Returns message in case of home page rendered
            }

            else {                                // All other cases
                $("#result").empty()
                $('#message').text(message)
                
                $("#result").append('<p><b>ARP records:</b></p>')
                for (step = 0; step < arp.length; step++){
                    $('#result').append('<pre>  ' + arp[step] + '</pre>')
                }

                $("#result").append('<p><b>DHCP records:</b></p>')
                for (step = 0; step < dhcp.length; step++){
                    $('#result').append('<pre>  ' + dhcp[step] + '</pre>')
                }

                $("#result").append('<p><b>ACL records</b></p>')
                for (step = 0; step < acl.length; step++){
                    $('#result').append('<pre>  ' + acl[step] + '</pre>')
                }
            }

        }
        
    } //close function

    // Submit post on submit
    $('form').on('submit', function(event) {
        event.preventDefault()
        $.ajax({
            url: '',
            type: 'post',
            data: $(this).serializeArray(),
            success: displayResponse
        }); //close ajax block
        
    }); //close form submit block

});
